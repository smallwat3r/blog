-- Pandoc Lua filter for blog post transformations.
--
-- Transforms:
--   CodeBlock: Wraps in div with copy button (click handler in blog.js)
--   Div: Converts djot sections to <section> elements with anchor links

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

  local header = el.content[1]
  if header and header.t == "Header" then
    header.identifier = el.identifier
    header.content = {pandoc.Link(header.content, "#" .. el.identifier)}
  end

  return wrap('<section id="' .. el.identifier .. '">', el.content, '</section>')
end
