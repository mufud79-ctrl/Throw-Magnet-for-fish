--!nonstrict
-- Demo: Q / E pick a move, F casts it (through the server so everyone sees it). Remove in production.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local Players = game:GetService("Players")
local StarterGui = game:GetService("StarterGui")

local effects = ReplicatedStorage:WaitForChild("AnimeVFX"):WaitForChild("Effects")
local request = ReplicatedStorage:WaitForChild("AnimeVFXRequest")
local names = {}
for _, m in ipairs(effects:GetChildren()) do
	table.insert(names, m.Name)
end
table.sort(names)
local index = 1

local gui = Instance.new("ScreenGui")
gui.Name = "AnimeVFXDemo"
gui.ResetOnSpawn = false
local label = Instance.new("TextLabel")
label.Size = UDim2.new(0, 420, 0, 36)
label.Position = UDim2.new(0.5, -210, 1, -60)
label.BackgroundTransparency = 0.35
label.BackgroundColor3 = Color3.fromRGB(16, 18, 26)
label.TextColor3 = Color3.new(1, 1, 1)
label.Font = Enum.Font.GothamBold
label.TextSize = 18
label.Parent = gui
gui.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")

local function refresh()
	label.Text = string.format("[Q/E] %s  [F] cast  (%d/%d)", names[index] or "none", index, #names)
end
refresh()

UserInputService.InputBegan:Connect(function(input, processed)
	if processed or #names == 0 then
		return
	end
	if input.KeyCode == Enum.KeyCode.E then
		index = index % #names + 1
		refresh()
	elseif input.KeyCode == Enum.KeyCode.Q then
		index = (index - 2) % #names + 1
		refresh()
	elseif input.KeyCode == Enum.KeyCode.F then
		request:FireServer(names[index])
	end
end)
