import Pkg
Pkg.add("Arrow")
Pkg.add("JuMP")
Pkg.add("HiGHS")
Pkg.add("SparseArrays")

# This code defines a function to solve a linear programming problem

using Arrow, JuMP, HiGHS, SparseArrays

"""
    maximize cᵀ·v 
    subject to S * v .== 0
              lb .<= v .<= ub
    """
function solve_cobra_fba(S_row_b::Vector{UInt8}, S_col_b::Vector{UInt8}, S_data_b::Vector{UInt8},
    nrow::Int, ncol::Int,
    lb_b::Vector{UInt8}, ub_b::Vector{UInt8}, c_b::Vector{UInt8})
    # 解码 IPC 字节为表格
    println("Before decoding arrow")
    S_row = collect(Arrow.Table(IOBuffer(S_row_b)).row)
    S_col = collect(Arrow.Table(IOBuffer(S_col_b)).col)
    S_data = collect(Arrow.Table(IOBuffer(S_data_b)).data)
    lb = collect(Arrow.Table(IOBuffer(lb_b)).lb)
    ub = collect(Arrow.Table(IOBuffer(ub_b)).ub)
    c = collect(Arrow.Table(IOBuffer(c_b)).c)

    S = sparse(S_row .+ 1, S_col .+ 1, S_data, nrow, ncol)

    # println("type of input", typeof(S), typeof(lb), typeof(ub), typeof(c))
    # println("size of input: ", size(S), length(lb), length(ub), length(c))
    # println("S: ", S)
    # println("lb: ", lb)
    # println("ub: ", ub)
    # println("c: ", c)
    
    model = Model(HiGHS.Optimizer)
    println("Before variable setting")
    @variable(model, lb[i] <= v[i=1:ncol] <= ub[i])
    println("Before objective setting")
    @objective(model, Max, sum(c[i] * v[i] for i in 1:ncol))
    println("Before constraint setting")
    JuMP.add_constraint(model, S * v .== 0)
    println("Before optimize call")
    optimize!(model)

    return value.(v)
end

function get_from_python(S_row_b::Any, S_col_b::Any, S_data_b::Any,
    nrow::Any, ncol::Any,
    lb_b::Any, ub_b::Any, c_b::Any)
    # print type
    # println("S_row_b type: ", typeof(S_row_b))
    # println("S_col_b type: ", typeof(S_col_b))
    # println("S_data_b type: ", typeof(S_data_b))
    # println("nrow type: ", typeof(nrow))
    # println("ncol type: ", typeof(ncol))
    # println("lb_b type: ", typeof(lb_b))
    # println("ub_b type: ", typeof(ub_b))
    # println("c_b type: ", typeof(c_b))
    # 调用 solve_cobra_fba 函数
    # 将 Python 的字节数组转换为 Julia 的 Vector{UInt8}
    S_row_b = Vector{UInt8}(S_row_b)
    S_col_b = Vector{UInt8}(S_col_b)
    S_data_b = Vector{UInt8}(S_data_b)
    lb_b = Vector{UInt8}(lb_b)
    ub_b = Vector{UInt8}(ub_b)
    c_b = Vector{UInt8}(c_b)
    nrow = Int(nrow)
    ncol = Int(ncol)

    println("Calling solve_cobra_fba with the provided parameters...")
    # 调用 solve_cobra_fba 函数
    result = solve_cobra_fba(S_row_b, S_col_b, S_data_b, nrow, ncol, lb_b, ub_b, c_b)
    # # 返回结果
    return result
end


# test locally
# include("load.jl")
# Pkg.add("MAT")
# using MAT

# model = loadModel("e_coli_core.mat", "e_coli_core")
# # println("type of model: ", typeof(model))
# # # print the keys of the model
# # println("keys of model: ", keys(model))
# # get 
# S = model[:S]
# ncol = size(S, 2)
# lb = model[:lb]
# ub = model[:ub]
# c = model[:c]

# model = Model(HiGHS.Optimizer)
# @variable(model, lb[i] <= v[i=1:ncol] <= ub[i])
# @objective(model, Max, sum(c[i] * v[i] for i in 1:ncol))
# @constraint(model, S * v .== 0)
# optimize!(model)

# # print the result
# println("result: ", value.(v))

