-- lua filter for spell checking: requires 'aspell'.
-- Copyright (C) 2017-2020 John MacFarlane, released under MIT license

-- pandoc.utils.stringify works on MetaValue elements since pandoc 2.1
if PANDOC_VERSION == nil then -- if pandoc_version < 2.1
  error("ERROR: pandoc >= 2.1 required for spellcheck.lua filter")
end

local path = require 'pandoc.path'
local text = require('text')
local words = {}
local deflang

local log_file_path = "out\\logs\\spellcheck_log.txt"

local logfile = io.open(log_file_path, "a")
for i, input_file in ipairs(PANDOC_STATE.input_files) do
  logfile:write("" .. input_file .. "\n")
end
logfile:close()


local function add_to_dict(lang, t)
  if not words[lang] then
    words[lang] = {}
  end
  if not words[lang][t] then
    words[lang][t] = (words[lang][t] or 0) + 1
  end
end

local function get_deflang(meta)
  deflang = (meta.lang and pandoc.utils.stringify(meta.lang)) or 'en'
  return {} -- eliminate meta so it doesn't get spellchecked
end

local function run_spellcheck(lang)
  local file = io.open(log_file_path, "a")
  io.output(file)
  local keys = {}
  local wordlist = words[lang]
  for k,_ in pairs(wordlist) do
    keys[#keys + 1] = k
  end
  local inp = table.concat(keys, '\n')
  local outp = pandoc.pipe('aspell', {'list','-l',lang, '-encoding', 'utf-8'}, inp)
  for w in string.gmatch(outp, "([%S]+)") do
    io.write(w)
    if lang ~= deflang then
      io.write("\t[" .. lang .. "]")
    end
    io.write("\n")
  end
  io.close(file)
end

local function results(el)
    pandoc.walk_block(pandoc.Div(el.blocks), {Str = function(e) add_to_dict(deflang, e.text) end})
    for lang,v in pairs(words) do
        run_spellcheck(lang)
    end
    os.exit(0)
end

local function checkstr(el)
  add_to_dict(deflang, el.text)
end

local function checkspan(el)
  local lang = el.attributes.lang
  if not lang then return nil end
  pandoc.walk_inline(el, {Str = function(e) add_to_dict(lang, e.text) end})
  return {} -- remove span, so it doesn't get checked again
end

local function checkdiv(el)
  local lang = el.attributes.lang
  if not lang then return nil end
  pandoc.walk_block(el, {Str = function(e) add_to_dict(lang, e.text) end})
  return {} -- remove div, so it doesn't get checked again
end

return {{Meta = get_deflang},
        {Div = checkdiv, Span = checkspan},
        {Str = function(e) add_to_dict(deflang, e.text) end, Pandoc = results}}