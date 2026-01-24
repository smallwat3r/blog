VENV := .venv
PYTHON := $(VENV)/bin/python
BUILD := .build

BLOG_DJ := $(wildcard content/blog/*.dj)
BLOG_HTML := $(patsubst content/%.dj,$(BUILD)/%.html,$(BLOG_DJ))

ALL_HTML := $(BLOG_HTML) $(BUILD)/about.html $(BUILD)/index.html

.PHONY: all build clean

# Extract body after frontmatter and convert to HTML
define dj2html
	@mkdir -p $(dir $@)
	@awk '/^---$$/{n++; next} n>=2' $< | pandoc -f djot -t html --no-highlight -o $@
endef

all: build

$(VENV):
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -q jinja2

$(BUILD)/blog/%.html: content/blog/%.dj
	$(dj2html)

$(BUILD)/%.html: content/%.dj
	$(dj2html)

build: $(VENV) $(ALL_HTML)
	$(PYTHON) build.py

clean:
	rm -rf dist dist.zip $(BUILD) $(VENV) __pycache__
