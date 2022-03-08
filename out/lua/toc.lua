local link_to_toc = pandoc.Link({pandoc.Str '↑'}, '#TOC')

function add_toc (h)
	h.content = h.content .. {pandoc.Space(), link_to_toc}
	return h
end

return {{Header = add_toc}}