function gf_CopyTable(tbOrg)
    local tbSaveExitTable = {}
    local function _copy(object)
        if type(object) ~= "table" then
            return object;
        elseif tbSaveExitTable[object] then --检查是否有循环嵌套的table
            return tbSaveExitTable[object];
        end
        local tbNewTable = {};
        tbSaveExitTable[object] = tbNewTable;
        for index, value in pairs(object) do
            tbNewTable[_copy(index)] = _copy(value);    --要考虑用table作索引的情况
        end
        return setmetatable(tbNewTable, getmetatable(object));
    end
    return _copy(tbOrg);
end

function formJson(file, lua_table, indent)
    indent = indent or 0
    for k, v in pairs(lua_table) do
        if type(k) == "string" then
            k = string.format("%q", k)
        end
        local szSuffix = ""
        if type(v) == "table" then
            szSuffix = "{"
        end
        local szPrefix = string.rep("    ", indent)
        formatting = szPrefix..k.." : "..szSuffix
        if type(v) == "table" then
            file:write(formatting.."\n")
            formJson(file, v, indent + 1)
            file:write(szPrefix.."},".."\n")
        else
            local szValue = ""
            if type(v) == "string" then
                szValue = string.format("%q", v)
            else
                szValue = tostring(v)
            end
            file:write(formatting..szValue..",".."\n")
        end
    end
end

function generatefile(filename, tbProto)
    local prefix, suffix
    prefix = "/*\n" .. "Don\'t modify this file manually!\n" .. "*/\n" .. "var _p = {\n"
    suffix = "\n};\n" .. "module.exports = _p;\n"

    local luaFile = io.open(filename, 'w')
    luaFile:write(prefix)
    formJson(luaFile, tbProto, 1)
    luaFile:write(suffix)
    luaFile:close()
end

os.execute('dir /s > temp.txt')
io.input('temp.txt')
for line in io.lines() do
    local pos, _, filename, ext = string.find(line, "^%d%d%d%d%-%d%d%-%d%d%s-%d%d:%d%d%s-[%d%,]+%s+(.+)%.(.+)%s-$");
    if pos and ext == 'lua' and filename ~= 'table2js' then
        print(filename, ext)
        local t = require(filename)
        generatefile(filename..'.js', t)
    end
end
