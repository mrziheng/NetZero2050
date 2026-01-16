import sys
import os
import time

# NOTE: This script uses Gurobi (gurobipy). 
# If you are using CPLEX or another solver, please adapt the import and model creation steps.

try:
    import gurobipy as gp
    from gurobipy import GRB
except ImportError:
    print("Error: 'gurobipy' library not found.")
    print("Please install it via: pip install gurobipy")
    print("Note: You also need a valid Gurobi license installed on your machine.")
    sys.exit(1)

def solve_lp_file(lp_file_path, log_file_path="solver.log"):
    """
    Reads a .lp file, optimizes it using Gurobi, and prints the status.
    """
    print(f"\n{'='*60}")
    print(f"--- GISPO Model Solver Tool ---")
    print(f"Target File: {lp_file_path}")
    print(f"{'='*60}\n")
    
    # 1. Validation
    if not os.path.exists(lp_file_path):
        print(f"[Error] File not found: {lp_file_path}")
        print("Please check the path and try again.")
        return

    try:
        # 2. Setup Environment
        # empty=True allows us to set parameters before starting the environment
        env = gp.Env(empty=True)
        env.setParam("LogFile", log_file_path)
        # Suppress console output slightly if needed, or keep verbose (1)
        env.setParam("OutputFlag", 1) 
        env.start()

        # 3. Load Model
        print(f"[Status] Reading LP file... (Please wait, large files take time)")
        start_read = time.time()
        model = gp.read(lp_file_path, env=env)
        read_time = time.time() - start_read
        print(f"[Status] Model loaded in {read_time:.2f} seconds.")
        print(f"         - Variables: {model.NumVars}")
        print(f"         - Constraints: {model.NumConstrs}")

        # 4. Configuration (Optional Performance Tuning)
        # For large energy models, the Barrier method (Method=2) is often fastest
        # model.setParam('Method', 2) 
        
        # 5. Optimization
        print("[Status] Beginning optimization...")
        start_solve = time.time()
        model.optimize()
        solve_time = time.time() - start_solve

        # 6. Result Handling
        print(f"\n{'='*60}")
        if model.Status == GRB.OPTIMAL:
            print(f"[Result] Optimization Successful!")
            print(f"         Objective Value: {model.ObjVal:e}")
            print(f"         Solve Time: {solve_time:.2f} seconds")
            
            # Optional: Save solution
            # sol_file = lp_file_path + ".sol"
            # model.write(sol_file)
            # print(f"         Solution written to: {sol_file}")
            
        elif model.Status == GRB.INF_OR_UNBD:
            print("[Result] Model is Infeasible or Unbounded.")
        elif model.Status == GRB.INFEASIBLE:
            print("[Result] Model is Infeasible.")
        elif model.Status == GRB.UNBOUNDED:
            print("[Result] Model is Unbounded.")
        else:
            print(f"[Result] Optimization stopped with status code: {model.Status}")
        print(f"{'='*60}\n")

    except gp.GurobiError as e:
        print(f"[Gurobi Error] Code {e.errno}: {e}")
    except Exception as e:
        print(f"[System Error] {e}")

if __name__ == "__main__":
    # --- DEFAULT CONFIGURATION ---
    # We default to the smallest file for the demo
    DEFAULT_FILE = "GISPO_LP/partial_8.lp" 
    
    target_file = DEFAULT_FILE

    # Check command line arguments
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        print(f"No file specified. Attempting to run default demo: {DEFAULT_FILE}")
        print("Usage: python solve_gispo_lp.py <path_to_lp_file>")

    solve_lp_file(target_file)