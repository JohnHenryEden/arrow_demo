from scipy.io import loadmat
from io import BytesIO
from scipy import sparse
import numpy as np
from objects.engine_model import EngineModel
import pyarrow as pa

# file = request.files["matfile"]通过表单字段名获取上传的文件,然后file_bytes = file.read()读取为二进制内容（bytes）
# 再调用这个方法build一个EngineModel
def load_model_from_mat(file_bytes: bytes) -> 'EngineModel':
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.loadmat.html
    data = loadmat(BytesIO(file_bytes))        # 使用 BytesIO 构造 file-like 对象并反序列化 .mat

    # 提取model名称，除了'__header__', '__version__', '__globals__'之外的就是模型名称
    model_names = [key for key in data.keys() if not key.startswith('__')]
    model_name = model_names[0]
    model_data = data[model_name]
    print(f"Model data keys: {model_data.dtype.names}")
    
    # 提取模型数据
    S =  sparse.csc_matrix(model_data['S'][0, 0])
    lb = np.array(_cell_to_float_list(model_data['lb'][0, 0]))
    ub = np.array(_cell_to_float_list(model_data['ub'][0, 0]))
    c = np.array(_cell_to_float_list(model_data['c'][0, 0]))
    b = np.array(_cell_to_float_list(model_data['b'][0, 0]))
    rxns = _cell_to_str_list(model_data['rxns'][0, 0])
    mets = _cell_to_str_list(model_data['mets'][0, 0])
    csense = _cell_to_str_list(model_data['csense'][0, 0]) if 'csense' in model_data.dtype.names else None
    
    # osense 可能是字符串 "max"/"min" 或数值 1/-1
    if "osenseStr" in model_data.dtype.names:
        val = model_data["osenseStr"][0, 0][0]
        osense = str(val) if isinstance(val, str) else str(val[0])
    elif "osense" in model_data.dtype.names:
        print(f"osense: {model_data['osense']}")
        val = float(model_data["osense"][0, 0][0][0])
        osense = "min" if val == 1 else "max"
    else:
        osense = "max"  # 默认方向
        
    # convert to pyarrow RecordBatch
    S_coo = S.tocoo()  # 转换为 COO 格式
    S = pa.RecordBatch.from_arrays(
        [
            pa.array(S_coo.row.astype(np.int32)),  # 行索引
            pa.array(S_coo.col.astype(np.int32)),  # 列索引
            pa.array(S_coo.data.astype(np.float64))                    # 数据值
        ],
        schema=pa.schema([
            ('row', pa.int32()),
            ('col', pa.int32()),
            ('data', pa.float64())
        ])
    )
    b = pa.array(b, type=pa.float64())
    c = pa.array(c, type=pa.float64())
    lb = pa.array(lb, type=pa.float64())
    ub = pa.array(ub, type=pa.float64())
    csense = pa.array(csense, type=pa.string()) if csense is not None else None
    osense = pa.scalar(osense, type=pa.string())
    
    # 创建模型对象
    return EngineModel(model_name, S, b, c, lb, ub, osense, csense)



def _cell_to_str_list(arr):
    return [str(cell[0]) for cell in arr.squeeze()]

def _cell_to_float_list(arr):
    flat = np.atleast_1d(arr).squeeze()
    result = []
    for x in flat:
        try:
            val = float(x[0]) if isinstance(x, (np.ndarray, list)) else float(x)
            result.append(val)
        except Exception as e:
            print(f"Warning: cannot convert {x} to float: {e}")
            result.append(0.0)  
    return result


