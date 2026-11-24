--!nonstrict
-- Server side of AnimeVFX: decides, validates and broadcasts. It never builds effects (clients do).
-- Gameplay (damage, knockback, hitboxes) stays here and never waits on an effect.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

local event = Instance.new("RemoteEvent")
event.Name = "AnimeVFXEvent" -- server -> clients: play(name, castCFrame, caster, targets)
event.Parent = ReplicatedStorage

local request = Instance.new("RemoteEvent")
request.Name = "AnimeVFXRequest" -- demo only: client asks to cast a move
request.Parent = ReplicatedStorage

local Effects = ReplicatedStorage:WaitForChild("AnimeVFX"):WaitForChild("Effects")
local COOLDOWN = 0.6
local lastCast = {}

local function hipOffset(character)
	local hum = character:FindFirstChildOfClass("Humanoid")
	local root = character:FindFirstChild("HumanoidRootPart")
	return (hum and root) and (hum.HipHeight + root.Size.Y / 2) or 3
end

-- Broadcast an effect to every client. Call this from your combat code after the server accepts a move.
local function broadcast(name, caster, targets)
	local root = caster:FindFirstChild("HumanoidRootPart")
	if not root then
		return
	end
	local look = root.CFrame.LookVector * Vector3.new(1, 0, 1)
	local feet = root.Position - Vector3.new(0, hipOffset(caster), 0)
	event:FireAllClients(name, CFrame.lookAt(feet, feet + look.Unit), caster, targets or {})
end

-- Demo validation: known move, cooldown, alive caster; targets = humanoids in front within range.
request.OnServerEvent:Connect(function(player, name)
	if typeof(name) ~= "string" or not Effects:FindFirstChild(name) then
		return
	end
	local now = os.clock()
	if lastCast[player] and now - lastCast[player] < COOLDOWN then
		return
	end
	lastCast[player] = now
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if not root then
		return
	end
	local targets = {}
	for _, model in ipairs(workspace:GetDescendants()) do
		if model:IsA("Humanoid") and model.Parent ~= character then
			local r = model.Parent:FindFirstChild("HumanoidRootPart")
			if r then
				local rel = root.CFrame:PointToObjectSpace(r.Position)
				if rel.Z < 0 and rel.Magnitude < 40 then
					table.insert(targets, model.Parent)
				end
			end
		end
	end
	broadcast(name, character, targets)
end)

Players.PlayerRemoving:Connect(function(p)
	lastCast[p] = nil
end)


