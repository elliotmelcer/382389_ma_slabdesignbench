import nlopt

class NloptDirectLocalSearch:
    """
    Author: Max Dombrowski
    NLopt DIRECT wrapper around an IOHexperimenter problem.
    """

    def __init__(self, max_evaluations: int = 50):
        self.max_evaluations = int(max_evaluations)
        self.name = "NLOPT_DIRECT_L"
        self.info = "locally biased variant of DIviding RECTangles (DIRECT) algorithm for global optimization"

    def __call__(self, problem):
        # Dimension & bounds from IOH
        n = int(problem.meta_data.n_variables)
        lb = [float(problem.bounds.lb[i]) for i in range(n)]
        ub = [float(problem.bounds.ub[i]) for i in range(n)]

        # Choose a DIRECT variant (global, derivative-free)
        # GN_DIRECT_L is usually a good default.
        opt = nlopt.opt(nlopt.GN_DIRECT_L, n)

        opt.set_lower_bounds(lb)
        opt.set_upper_bounds(ub)

        def objective(x, grad):
            # DIRECT ignores grad; just comply with the signature.
            # Map floats to ints for IOH
            x_int = [int(round(xi)) for xi in x]
            y = problem(x_int)   # penalised objective
            return float(y)

        opt.set_min_objective(objective)
        opt.set_maxeval(self.max_evaluations)

        # Initial point (DIRECT is global, but NLopt wants a start point anyway)
        x0 = [(lo + hi) / 2.0 for lo, hi in zip(lb, ub)]

        try:
            x_best = opt.optimize(x0)
            f_best = float(opt.last_optimum_value())
        except nlopt.RoundoffLimited:
            # If DIRECT bails out with numerical issues, still grab the best seen
            x_best = opt.last_optimize_result()  # may not be super helpful, but keep structure
            f_best = float(opt.last_optimum_value())
        # (If you want to be strict, you can re-raise instead.)

        # Cast back to ints
        x_best_int = [int(round(xi)) for xi in x_best]

        # Keep IOH state consistent
        # problem(x_best_int)

        return f_best, x_best_int