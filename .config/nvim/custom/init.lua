-- example file i.e lua/custom/init.lua

-- MAPPINGS
vim.api.nvim_set_keymap("i", "<C-J>", 'copilot#Accept("<CR>")', { silent = true, expr = true })


-- Github copilot config
vim.g.copilot_no_tab_map = true

