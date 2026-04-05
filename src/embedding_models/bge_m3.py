from FlagEmbedding import BGEM3FlagModel


VECTOR_LENGTH = 1024


def initialize_model():
    """Initialize the BGE-M3 embedding model"""
    return BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)


if __name__ == "__main__":
    # check real vector length
    model = initialize_model()
    vector = model.encode("test", return_dense=True)
    print(vector)