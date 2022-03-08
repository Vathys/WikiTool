if PANDOC_VERSION == nil then -- if pandoc_version < 2.1
	error("ERROR: pandoc >= 2.1 required for spellcheck.lua filter")
end

local path = require('pandoc.path')
local text = require('text')
local words = {}

local log_file_path = "out\\logs\\spellcheck_log.txt"

local logfile = io.open(log_file_path, "a")
for i, input_file in ipairs(PANDOC_STATE.input_files) do
	logfile:write("" .. input_file .. "\n")
end
logfile:close()

function string.starts(String, Start)
	return string.sub(String, 1, string.len(Start)) == Start
end

function string.ends(String, End)
	return string.sub(String, -string.len(End), -1) == End
end

function detectZean_Str(el)
	local pre, tgt, post = el.text:match("(.*)%{%{(.+)%}%}(.*)")
	if tgt == null then
		return el
	else
		table.insert(words, tgt)
		
		if pre == null then 
			if post == null then
				return pandoc.Span(tgt, {class = 'zean'})
			else
				return {pandoc.Span(tgt, {class = 'zean'}), pandoc.Str(post)}
			end
		else
			if post == null then
				return {pandoc.Str(pre), pandoc.Span(tgt, {class = 'zean'})}
			else
				return {pandoc.Str(pre), pandoc.Span(tgt, {class = 'zean'}), pandoc.Str(post)}
			end
		end
	end
end

function detectZean_Inlines(inlines)
	local result = {}
	local local_words = {}
	local startword = false
	for i = 1, #inlines, 1 do
		if startword == false then
			local part_tgt = pandoc.utils.stringify(inlines[i]):match("%{%{(.+)")
			if part_tgt ~= null then
				table.insert(words, part_tgt)
				table.insert(local_words, part_tgt)
				startword = true
			else
				table.insert(result, inlines[i])
			end
		else 
			local part_tgt = pandoc.utils.stringify(inlines[i]):match("(.+)%}%}")
			if part_tgt == null then
				table.insert(words, pandoc.utils.stringify(inlines[i]))
				table.insert(local_words, pandoc.utils.stringify(inlines[i]))
			else
				table.insert(words, part_tgt)
				table.insert(local_words, part_tgt)
				table.insert(result, pandoc.Span(table.concat(local_words, ""), {class = "zean"}))
				local_words = {}
				startword = false
			end
		end
	end
	
	return result
end

function log_words(el) 
	local logfile = io.open(log_file_path, "a")
	for i, word in ipairs(words) do
		logfile:write(word .. "\n")
	end
end

return {{Str = detectZean_Str, Inlines = detectZean_Inlines, Pandoc = log_words}}