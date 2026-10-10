.PHONY: run test style demo vfs

run:
	./run.sh

test:
	PYTHONPATH=src:. python3 -m unittest discover -s tests -t . -v

style:
	python3 tools/check_style.py

vfs:
	python3 tools/make_vfs.py

demo:
	for script in scripts/*.sh; do echo "== $$script"; \
	    sh "$$script" < /dev/null; done
