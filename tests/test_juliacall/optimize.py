from juliacall import Main as jl
from io_utils import load_model_from_mat
import argparse



# 加载 Julia 逻辑
jl.include("solve_julia.jl")


file_path = 'D:\\Work\\Arrow-Demo\\sample\\e_coli_core.mat'
    
    
m = load_model_from_mat(file_path)
S_row_b, S_col_b, S_data_b,nrow, ncol,lb_b, ub_b, c_b = m.to_arrow()
result = jl.get_from_python(S_row_b, S_col_b, S_data_b,nrow, ncol,lb_b, ub_b, c_b)
print("call julia successfully")