local function has_value (tab, val)
    for index, value in ipairs(tab) do
        if pandoc.utils.stringify(value) == val then
            return true
        end
    end

    return false
end

return {
  {
    Para = function (elem)
      if has_value(elem.content, "---") then
        return pandoc.HorizontalRule()
	 elseif has_value(elem.content, "===") then
	   return {pandoc.HorizontalRule(), pandoc.HorizontalRule()}
      else
        return elem
      end
    end
  },
}