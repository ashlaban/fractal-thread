
ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
LOG_DIR:=$(ROOT_DIR)/log

PYTHON_INC_CC=-I/usr/local/Cellar/python3/3.4.2_1/Frameworks/Python.framework/Versions/3.4/Headers/
PYTHON_INC_LD=-L/usr/local/Cellar/python3/3.4.2_1/Frameworks/Python.framework/Versions/3.4/lib/
PYTHON_INC_LD+=-L$(OUT_DIR)
PYTHON_CC_FLAGS=-O2 -shared -fPIC
PYTHON_LD_FLAGS=-lpython3.4 -lf3c

INC_CC= 
INC_CC+=-Ic/
INC_CC+=-Ic/sse
INC_CC+=-Ic/avx
INC_LD=

LD_FLAGS= 
CC_FLAGS= -O2 -fPIC

OUT_DIR=c/out

f3c.so: LIB_F3C_CORE
	$(CC) -Ic $(PYTHON_INC_CC) $(PYTHON_INC_LD) $(PYTHON_CC_FLAGS) $(PYTHON_LD_FLAGS) -o $@ f3c.c

AVX: $(OUT_DIR)/libf3c-avx.o
SSE: $(OUT_DIR)/libf3c-sse.o
NO_EXT: $(OUT_DIR)/libf3c-no-ext.o
CORE: $(OUT_DIR)/libf3c-core.o
LIB_F3C_CORE: AVX SSE NO_EXT $(OUT_DIR)/libf3c.a

TEST: $(OUT_DIR)/f3c-test.o

$(OUT_DIR)/libf3c-avx.o: c/avx/f3c-avx.c
	$(CC) -c $(INC_CC) $(CC_FLAGS) -mavx2 $< -o $@
$(OUT_DIR)/libf3c-sse.o: c/sse/f3c-sse.c
	$(CC) -c $(INC_CC) $(CC_FLAGS) -msse2 $< -o $@
$(OUT_DIR)/libf3c-no-ext.o: c/f3c-no-ext.c
	$(CC) -c $(INC_CC) $(CC_FLAGS) $< -o $@
$(OUT_DIR)/libf3c-core.o: c/f3c-core.c
	$(CC) -c $(INC_CC) $(CC_FLAGS) $< -o $@

$(OUT_DIR)/libf3c.a: $(OUT_DIR)/libf3c-no-ext.o $(OUT_DIR)/libf3c-sse.o $(OUT_DIR)/libf3c-avx.o $(OUT_DIR)/libf3c-core.o
	ar cr $@ $^

$(OUT_DIR)/f3c-test.o: c/f3c-test.c
	$(CC) $(INC_CC) $(CC_FLAGS) $< -o $@

# ========== MANAGEMENT ============
start-all: start-compute-server start-web-server start-compute-client
start-web-server:
	cd ../frontend; python3 ../backend/fracthWebServer.py &> $(LOG_DIR)/fracth-web-server.log &
start-compute-server:
	python3 fracthComputeServer.py &> $(LOG_DIR)/fracth-compute-server.log &
start-compute-client:
	python3 fracthComputeClient.py &> $(LOG_DIR)/fracth-compute-client.log &