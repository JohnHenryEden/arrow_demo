import unittest
import utils.mat_parser as parser

def test_mat_parser():
    with open("sample\\e_coli_core.mat", "rb") as file:
        model_bin = file.read()
        data = parser.load_model_from_mat(model_bin)
        ipc = data.to_ipc_bytes()
        print(ipc)