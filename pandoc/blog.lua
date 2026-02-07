-- Pandoc Lua filter for blog post transformations.
--
-- Transforms:
--   Image: Copies alt text to title attribute for hover tooltips
--   CodeBlock: Wraps in div with copy button (click handler in blog.js)
--   Div: Converts djot sections to <section> elements with anchor links
--   Link: Adds "external" class to external links

local function html(s)
  return pandoc.RawBlock("html", s)
end

local function wrap(open, content, close)
  local blocks = {html(open)}
  for _, block in ipairs(content) do
    blocks[#blocks + 1] = block
  end
  blocks[#blocks + 1] = html(close)
  return blocks
end

-- Adds "external" class to links pointing outside the blog.
function Link(el)
  if el.target:match("^https?://") then
    el.classes:insert("external")
  end
  return el
end

-- Sets image title from alt text so it shows on hover.
function Image(el)
  local alt = pandoc.utils.stringify(el.caption)
  if alt ~= "" then
    el.title = alt
  end
  return el
end

-- Wraps code blocks in a div with a copy button.
-- Click handler is in blog.js.
function CodeBlock(el)
  return {
    html('<div class="pre-wrapper">'),
    el,
    html('<span class="copy-btn">copy</span>'),
    html('</div>')
  }
end

-- Converts djot section divs to HTML <section> elements.
-- Adds anchor links to headings and restores header IDs for TOC.
function Div(el)
  if not el.classes:includes("section") or el.identifier == "" then
    return el
  end

  local id = el.identifier:lower()

  local header = el.content[1]
  if header and header.t == "Header" then
    header.identifier = id
    header.content = {pandoc.Link(header.content, "#" .. id)}
  end

  return wrap('<section id="' .. id .. '">', el.content, '</section>')
end
