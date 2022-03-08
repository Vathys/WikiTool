local path = require 'pandoc.path'

local base_out = ""

function string.starts(String, Start)
	return string.sub(String, 1, string.len(Start)) == Start
end

function get_base_out(meta)
	if meta.link_base ~= nil then
		base_out = meta.link_base
	end
end

function add_base_out_link(el)
	if string.starts(el.target, ".\\") or string.starts(el.target, "https://") then
		el.target = path.normalize(el.target)
	else 
		el.target = path.normalize(path.join({base_out, el.target}))
	end
	return el
end

function add_base_out_image(el)
	el.src = path.normalize(path.join({base_out, el.src}))
	return el
end

return {
	{Meta = get_base_out},
	{Link = add_base_out_link, Image = add_base_out_image}
}