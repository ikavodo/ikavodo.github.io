# scripts/compare_2dof.py
from typing import Dict, Tuple, Any
import torch
from scripts.plot_helpers import plot_metric_vs_density_ci, plot_time_to_threshold_ci
from src.draw import draw_shape
from scripts.utils import get_shift_grid, run_multi_seed_backbone, motion_params_from_shifts, \
    initialize_shifts_per_sample, save_video, epe
from src.optimization import spatial_pipeline, fourier_pipeline, gcc_phat_pipeline
from src.utils import motion_bounds, build_mask, make_motion_videos
from src.occluders import Occluder

# globals if run from outside script
H, W = 128, 128
T = 8
SHIFT_SCALE = max(H, W) // (5 * T)
SHIFT_RANGE = 2 * SHIFT_SCALE
SUCCESS_CRIT = 0.5
MARGIN_WIDTH = 0.2  # or 0.375
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
N_RUNS = 3
LR = 1.
OCCLUDER_MODE = Occluder.TRIANGULAR


# test modes: toggle occluders and margin
def compute_motion_on_grid_batched(
        method: str,
        density: float,
        max_steps: int = 300,
        step_cutoff: int = 5,
        use_bounds: bool = False,
        seed_offset: int = 0,
        plot=False,
        occluder_mode=OCCLUDER_MODE,
        margin_width=MARGIN_WIDTH,
        occluder_val=0.5
):
    shift_grid = list(get_shift_grid(SHIFT_RANGE, DEVICE))
    batch_size = len(shift_grid)
    all_trials = []
    successes = []

    for base in range(0, len(shift_grid), batch_size):
        chunk = shift_grid[base: base + batch_size]
        Bc = len(chunk)

        # ---- stack shifts -> (Bc, 2) ----
        shifts0 = torch.cat(
            [s.reshape(1, -1) if s.ndim == 1 else s for s in chunk],
            dim=0
        ).to(DEVICE)

        motion_params = motion_params_from_shifts(shifts0, Bc, DEVICE)
        shifts = motion_params[:, :2]
        rot_scale = motion_params[:, -2:]
        gt_motion_params = torch.cat([-shifts, rot_scale], dim=-1)  # (Bc, 4)
        gt_shifts = gt_motion_params[:, :2]  # (Bc, 2)

        # ---- build frames for this chunk (Bc, ...) ----
        # frames is (1, H, W) or (1, 1, H, W) depending on draw_shape; keep your original.
        # frames: DO NOT expand()
        frames, _ = draw_shape((1, H, W), device=DEVICE, margin_width=margin_width)

        if frames.ndim == 3:
            frames_chunk = frames.repeat(Bc, 1, 1).contiguous()
        else:
            frames_chunk = frames.repeat(Bc, *([1] * (frames.ndim - 1))).contiguous()

        # batched videos in ONE call (per-sample seed via seed+i inside draw_occluders_tri)
        seed0 = base + seed_offset

        videos = make_motion_videos(
            frames_chunk, T, motion_params,
            differentiable_shift=False,
            density=float(density),
            occluder_mode=occluder_mode,
            occluded=True,
            occluder_val=occluder_val,
            seed=seed0,
            tol=0.03,
        )
        if plot and base == batch_size:
            save_video(videos[0:1, ...], sub_dir_name="translation", ending=f"_video.mp4", fps=5)

        # ---- params to optimize ----

        # freeze input; we only optimize init_shifts
        input_spatial = videos.detach()

        if method == "fourier" or method == "gcc_phat":
            # put this inside (fourier/gcc_phat)_pipeline to match func signatures
            if use_bounds:
                bounds = motion_bounds(input_spatial)
                spatial_mask = build_mask(bounds, input_spatial)
                input_spatial = input_spatial * spatial_mask

            input_fourier = torch.fft.fft2(input_spatial, norm="forward", dim=(-2, -1)).detach()

            if method == "fourier":
                # check if works for IIR, lanczos
                pipeline_fn = lambda cur_mp: fourier_pipeline(input_fourier, cur_mp, weighted_var=True)
            elif method == "gcc_phat":
                pipeline_fn = lambda cur_mp: gcc_phat_pipeline(input_fourier, cur_mp)
            else:
                raise ValueError(f"Unknown method {method}")
        else:
            pipeline_fn = lambda cur_mp: spatial_pipeline(input_spatial, cur_mp, use_bounds=use_bounds)

        init_shifts = initialize_shifts_per_sample(SHIFT_SCALE, Bc, DEVICE, seed0)
        optimizer = torch.optim.Adam([init_shifts], lr=LR)

        deviations_per = [[] for _ in range(Bc)]
        all_shifts_per = [[] for _ in range(Bc)]
        converged = torch.zeros(Bc, dtype=torch.bool, device=DEVICE)
        time_to_thresh = torch.full((Bc,), max_steps + 1, dtype=torch.long, device=DEVICE)

        for step in range(max_steps):
            cur_motion_params = torch.cat([init_shifts, rot_scale], dim=-1)  # (Bc,4)

            optimizer.zero_grad(set_to_none=True)
            _, var_batches = pipeline_fn(cur_motion_params)

            # IMPORTANT: keep loss separable per sample; sum is fine
            var_batches = var_batches.squeeze()  # -> (Bc,)
            loss = -var_batches.sum()
            loss.backward()
            optimizer.step()

            cur = init_shifts.detach()
            error = epe(cur, gt_shifts)

            for i in range(Bc):
                deviations_per[i].append(float(error[i].item()))
                all_shifts_per[i].append(cur[i:i + 1].clone())

            newly = (~converged) & (step >= step_cutoff) & (error < SUCCESS_CRIT)
            if newly.any():
                converged |= newly
                time_to_thresh[newly] = step + 1

            if bool(converged.all()):
                break

        for i in range(Bc):
            trial = {
                "converged": bool(converged[i].item()),
                "time_to_thresh": int(time_to_thresh[i].item()),
                "deviations": deviations_per[i],
                "all_shifts": all_shifts_per[i],
                "final_shifts": all_shifts_per[i][-1],
                "gt_shifts": gt_shifts[i:i + 1].detach(),
            }
            all_trials.append(trial)
            successes.append(trial["converged"])

    success_rate = float(sum(successes) / len(successes)) if successes else 0.0
    return all_trials, success_rate


def eval_fn_compare_pipelines(
        density: float,
        seed_offset: int = 0,
        use_bounds: bool = False,
        max_steps: int = 300,
        step_cutoff: int = 20,
        plot=False,
        occluder_mode=None,
        occluder_val=0.5,
        margin_width=None,
        methods=("spatial", "fourier", "gcc_phat"),  # all
) -> Tuple[Dict[str, Any], Dict[str, float], Dict[str, float]]:
    """
    Returns:
      results_at_d: {"spatial": trials, "fourier": trials}
      success_at_d: {"spatial": success_rate, "fourier": success_rate}
      ttt_at_d:     {"spatial": median_time_to_thresh, "fourier": median_time_to_thresh}
    """
    results_at_d: Dict[str, Any] = {}
    success_at_d: Dict[str, float] = {}
    ttt_at_d: Dict[str, float] = {}
    occluder_mode = OCCLUDER_MODE if occluder_mode is None else occluder_mode
    margin_width = MARGIN_WIDTH if margin_width is None else margin_width
    for method in methods:
        trials, rate = compute_motion_on_grid_batched(
            method=method,
            density=float(density),
            max_steps=max_steps,
            step_cutoff=step_cutoff,
            use_bounds=use_bounds,
            seed_offset=seed_offset,
            plot=plot,
            margin_width=margin_width,
            occluder_mode=occluder_mode,
            occluder_val=occluder_val
        )
        results_at_d[method] = trials
        success_at_d[method] = float(rate)

        # median time-to-threshold over grid trials (robust)
        ttts = [t["time_to_thresh"] for t in trials]
        ttt_at_d[method] = float(torch.median(torch.tensor(ttts)))

    return results_at_d, success_at_d, ttt_at_d


if __name__ == "__main__":
    step = 0.1
    end = 0.9
    densities = torch.linspace(0., end, round(end / step) + 1)
    methods = ["spatial", "fourier"]
    plot = True
    # (1) optimization pipeline
    runs_opt, success_opt, ttt_opt = run_multi_seed_backbone(
        densities=densities,
        n_runs=N_RUNS,
        run_seed0=0,
        eval_fn=eval_fn_compare_pipelines,
        eval_kwargs={
            "max_steps": 250,
            "step_cutoff": 20,
            "occluder_mode": OCCLUDER_MODE,
            "occluder_val": 0.,  # subtracted static occluders
            "margin_width": MARGIN_WIDTH,
            "methods": methods,
        },
        methods=methods
    )
    if plot:
        # 2) Plot success rate vs density, or save it! Even better
        plot_metric_vs_density_ci(
            densities=densities,
            stack=success_opt,
            methods=methods,
            ylabel="Success rate (EPE < 0.5)",
            save_dir="results",
            stem="success_vs_density",
            ylim=(0, 1.05),
            legend_loc="lower left",
            title="2DoF success rate vs occlusion density"
        )

        # 3) Plot time-to-threshold vs density
        plot_time_to_threshold_ci(
            densities=densities,
            ttt_stack=ttt_opt,
            methods=methods,
            save_dir="results",
            stem="time_to_threshold_vs_density",
            title="2DoF time-to-threshold vs. occlusion density"
        )
