VENV := .venv
PYTHON := $(VENV)/bin/python
BUILD := .build

BLOG_DJ := $(wildcard content/blog/*.dj)
BLOG_HTML := $(patsubst content/%.dj,$(BUILD)/%.html,$(BLOG_DJ))

ALL_HTML := $(BLOG_HTML) $(BUILD)/about.html $(BUILD)/cv.html $(BUILD)/index.html

PANDOC_VERSION := 3.10.2
PANDOC_BIN := $(shell command -v pandoc || echo $(BUILD)/bin/pandoc)
PANDOC := $(PANDOC_BIN) -f djot -t html
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

# Cloudflare's build image has no pandoc, grab the static binary
$(BUILD)/bin/pandoc:
	mkdir -p $(dir $@)
	curl -fsSL https://github.com/jgm/pandoc/releases/download/$(PANDOC_VERSION)/pandoc-$(PANDOC_VERSION)-linux-amd64.tar.gz \
	  | tar xz -C $(dir $@) --strip-components=2 --wildcards '*/bin/pandoc'

$(BUILD)/blog/%.html: content/blog/%.dj pandoc/template.html pandoc/blog.lua | $(PANDOC_BIN)
	$(frontmatter) | $(PANDOC) $(BLOG_OPTS) -o $@

$(BUILD)/%.html: content/%.dj | $(PANDOC_BIN)
	$(frontmatter) | $(PANDOC) -o $@

build: $(VENV) $(ALL_HTML)
	$(PYTHON) build.py

clean:
	rm -rf dist dist.zip $(BUILD) __pycache__
