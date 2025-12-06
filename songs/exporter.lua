script_name = "Export karaoke JSON (from \\k tags)"
script_description = "Export per-word karaoke timing as JSON, grouped by line, using raw \\k tags"
script_author = "ChatGPT"
script_version = "0.3"

-- Basic JSON string escaper (enough for lyrics)
local function json_escape(str)
    if not str then return "" end
    str = str:gsub("\\", "\\\\")
    str = str:gsub("\"", "\\\"")
    str = str:gsub("\b", "\\b")
    str = str:gsub("\f", "\\f")
    str = str:gsub("\n", "\\n")
    str = str:gsub("\r", "\\r")
    str = str:gsub("\t", "\\t")
    return str
end

-- Parse a single ASS karaoke line's text into syllables based on \k tags.
-- Returns a list of { rel_start, rel_end, text } where rel_* are in ms
local function parse_k_syllables(text)
    local syllables = {}
    local total_cs = 0  -- accumulated centiseconds from start of line
    local i = 1
    local len = #text

    while true do
        -- find a \kNNN tag
        local tag_start, tag_end, dur_str = text:find("\\k(%d+)", i)
        if not tag_start then
            break
        end

        -- we assume this \k is inside a {...} block; find closing brace
        local brace_end = text:find("}", tag_end + 1)
        if not brace_end then
            -- malformed line; bail out
            break
        end

        -- syllable text runs from end of brace to before next '{' or end-of-line
        local next_brace = text:find("{", brace_end + 1)
        if not next_brace then
            next_brace = len + 1
        end

        local syl_text = text:sub(brace_end + 1, next_brace - 1)
        -- trim whitespace
        syl_text = syl_text:gsub("^%s+", ""):gsub("%s+$", "")

        local dur_cs = tonumber(dur_str) or 0
        local start_ms = total_cs * 10
        local end_ms   = (total_cs + dur_cs) * 10
        total_cs = total_cs + dur_cs

        if syl_text:match("%S") and dur_cs > 0 then
            table.insert(syllables, {
                rel_start = start_ms,
                rel_end   = end_ms,
                text      = syl_text
            })
        end

        i = next_brace
        if i > len then
            break
        end
    end

    return syllables
end

local function export_karaoke_json(subs, sel)
    local chunks = {}
    table.insert(chunks, "[\n")
    local first_output_line = true

    -- If the user selected lines, only process those; else process all dialogue lines
    local line_indices = {}
    if #sel > 0 then
        for _, i in ipairs(sel) do
            table.insert(line_indices, i)
        end
    else
        for i = 1, #subs do
            local line = subs[i]
            if line.class == "dialogue" and not line.comment then
                table.insert(line_indices, i)
            end
        end
    end

    for _, idx in ipairs(line_indices) do
        local line = subs[idx]
        if line.class == "dialogue" and not line.comment then
            -- Only bother with lines that actually have \k tags
            if not line.text:match("\\k%d+") then
                goto continue_line
            end

            local syllables = parse_k_syllables(line.text)

            if #syllables == 0 then
                goto continue_line
            end

            if not first_output_line then
                table.insert(chunks, ",\n")
            end
            first_output_line = false

            local line_start = line.start_time or 0
            local line_end   = line.end_time or (line_start + 0)

            table.insert(chunks, "  {\n")
            table.insert(chunks, "    \"line_index\": " .. idx .. ",\n")
            table.insert(chunks, "    \"start\": " .. line_start .. ",\n")
            table.insert(chunks, "    \"end\": " .. line_end .. ",\n")
            table.insert(chunks,
                "    \"text\": \"" .. json_escape(line.text) .. "\",\n")
            table.insert(chunks, "    \"words\": [\n")

            for si, syl in ipairs(syllables) do
                local abs_start = line_start + syl.rel_start
                local abs_end   = line_start + syl.rel_end

                local entry = string.format(
                    "      {\"start\": %d, \"end\": %d, \"text\": \"%s\"}",
                    abs_start, abs_end, json_escape(syl.text)
                )
                table.insert(chunks, entry)
                if si < #syllables then
                    table.insert(chunks, ",")
                end
                table.insert(chunks, "\n")
            end

            table.insert(chunks, "    ]\n")
            table.insert(chunks, "  }")
        end
        ::continue_line::
    end

    table.insert(chunks, "\n]\n")

    if first_output_line then
        aegisub.log("Export karaoke JSON: no lines with \\k timing found.\n")
        return
    end

    local filename = aegisub.dialog.save(
        "Export karaoke JSON",
        "lyrics.json",
        "",
        "JSON files (.json)|*.json|All files (.)|*.*",
        false
    )

    if not filename then
        return
    end

    local f, err = io.open(filename, "w")
    if not f then
        aegisub.log("Export karaoke JSON: could not open file: %s\n", tostring(err))
        return
    end

    f:write(table.concat(chunks))
    f:close()

    aegisub.set_undo_point(script_name)
end

aegisub.register_macro(
    script_name,
    script_description,
    export_karaoke_json
)
