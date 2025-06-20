from scipy.io import loadmat
from model import Model
import numpy as np
import numpy as np
from scipy import sparse

def load_model_from_mat(file_path: str):
    data = loadmat(file_path)
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
    rxns = _cell_to_str_list(model_data['rxns'][0, 0])
    mets = _cell_to_str_list(model_data['mets'][0, 0])
    csense = _cell_to_str_list(model_data['csense'][0, 0]) if 'csense' in model_data.dtype.names else None
    
    # osense 可能是字符串 "max"/"min" 或数值 1/-1
    if "osenseStr" in model_data.dtype.names:
        val = model_data["osenseStr"][0, 0][0]
        sense = str(val) if isinstance(val, str) else str(val[0])
    elif "osense" in model_data.dtype.names:
        print(f"osense: {model_data['osense']}")
        val = float(model_data["osense"][0, 0][0][0])
        sense = "min" if val == 1 else "max"
    else:
        sense = "max"  # 默认方向
        
    # 创建模型对象
    return Model(model_name, S, lb, ub, c, rxns, mets, sense, csense)



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
