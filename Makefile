VENV := .venv
PYTHON := $(VENV)/bin/python
BUILD := .build

BLOG_DJ := $(wildcard content/blog/*.dj)
BLOG_HTML := $(patsubst content/%.dj,$(BUILD)/%.html,$(BLOG_DJ))

ALL_HTML := $(BLOG_HTML) $(BUILD)/about.html $(BUILD)/index.html

PANDOC := pandoc -f djot -t html
BLOG_OPTS := --toc -s --template=pandoc/template.html --lua-filter=pandoc/blog.lua

.PHONY: all build clean

# Extract body after frontmatter (print before counting, so body '---' lines survive)
define frontmatter
@mkdir -p $(dir $@)
@awk 'n>=2; /^---$$/{n++}' $<
endef

all: build

$(VENV):
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -q jinja2

$(BUILD)/blog/%.html: content/blog/%.dj pandoc/template.html pandoc/blog.lua
	$(frontmatter) | $(PANDOC) $(BLOG_OPTS) -o $@

$(BUILD)/%.html: content/%.dj
	$(frontmatter) | $(PANDOC) -o $@

build: $(VENV) $(ALL_HTML)
	$(PYTHON) build.py

clean:
	rm -rf dist dist.zip $(BUILD) __pycache__
