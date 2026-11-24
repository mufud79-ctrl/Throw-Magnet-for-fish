--!nonstrict
-- Plays effects the server broadcasts. Camera shake / grade / impact frames only for nearby effects.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local AnimeVFX = require(ReplicatedStorage:WaitForChild("AnimeVFX"))
local event = ReplicatedStorage:WaitForChild("AnimeVFXEvent")

event.OnClientEvent:Connect(function(name, castCFrame, caster, targets)
	local cam = workspace.CurrentCamera
	local near = (cam.CFrame.Position - castCFrame.Position).Magnitude < 160
	AnimeVFX.Play(name, castCFrame, { caster = caster, targets = targets, camera = near })
end)
