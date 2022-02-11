.PHONY: init
init:
    pip install -r requirements.txt

.PHONY: test
test:
    py.test tests