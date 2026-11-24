--!nonstrict
--[[
	AnimeVFX runtime (client). Plays the same effect specs the headless previewer renders.

	Put this folder in ReplicatedStorage. Effects live in AnimeVFX.Effects (one ModuleScript per move, generated
	by scripts/export_luau.py), asset ids in AnimeVFX.Assets. Clients play effects; the server only decides and
	broadcasts (see Server/AnimeVFXServer.server.lua).

		local AnimeVFX = require(game.ReplicatedStorage.AnimeVFX)
		AnimeVFX.Play("000_FireFist", casterRoot.CFrame, { caster = character, targets = { enemyModel } })

	Coordinates in a spec are studs relative to the cast CFrame: the caster stands at the origin facing -Z
	(LookVector), Y up. Times are seconds from the cast.

	Animation rules built into playback:
	  * timing / hit-stop: spec.hitstop freezes effect time for a few frames on each hit. Emitters get
	    TimeScale = 0, shells/beams/numbers stop advancing, and the caster's and targets' AnimationTracks are
	    paused; camera shake keeps running.
	  * arcs: moving attachments follow spec arcs; sparks fall under Acceleration; damage numbers pop and arc.
	  * squash/stretch + follow-through are authored in the data (Squash sequences, shell scale keys, lagging
	    trails). Character wind-up / settle beats are in spec.pose as a guide for your AnimationTracks.
]]

local RunService = game:GetService("RunService")
local Lighting = game:GetService("Lighting")
local Players = game:GetService("Players")
local Workspace = game:GetService("Workspace")

local Assets = require(script:WaitForChild("Assets"))

local AnimeVFX = {}
AnimeVFX.Quality = 1 -- 0.3 .. 1, scales burst counts and rates (set from settings on mobile)
AnimeVFX.Folder = nil

local RAD = math.pi / 180

------------------------------------------------------------------------ helpers
local function folder()
	if AnimeVFX.Folder and AnimeVFX.Folder.Parent then
		return AnimeVFX.Folder
	end
	local f = Instance.new("Folder")
	f.Name = "AnimeVFX_Local"
	f.Parent = Workspace
	AnimeVFX.Folder = f
	return f
end

local function autoQuality()
	local ok, level = pcall(function()
		return UserSettings():GetService("UserGameSettings").SavedQualityLevel.Value
	end)
	if ok and level and level > 0 then
		return math.clamp(0.3 + level * 0.07, 0.3, 1)
	end
	return 1
end

local function v3(t)
	return Vector3.new(t[1], t[2], t[3])
end

local function lerp(a, b, k)
	return a + (b - a) * k
end

local function ease(k, e)
	if e == "out" then
		return 1 - (1 - k) * (1 - k)
	elseif e == "in" then
		return k * k
	elseif e == "outExpo" then
		return k >= 1 and 1 or 1 - 2 ^ (-10 * k)
	elseif e == "outBack" then
		return 1 + 2.7 * (k - 1) ^ 3 + 1.7 * (k - 1) ^ 2
	end
	return k
end

-- keys: number | {x,y,z} | { {k, value, ease?}, ... } where value is a number or {x,y,z}
local function isKeys(v)
	return type(v) == "table" and type(v[1]) == "table"
end

local function lerpValue(a, b, t)
	if type(a) == "table" then
		return { lerp(a[1], b[1], t), lerp(a[2], b[2], t), lerp(a[3], b[3], t) }
	end
	return lerp(a, b, t)
end

local function evalKeys(keys, k, default)
	if keys == nil then
		return default
	end
	if not isKeys(keys) then
		return keys
	end
	if k <= keys[1][1] then
		return keys[1][2]
	end
	for i = 2, #keys do
		local b = keys[i]
		if k <= b[1] then
			local a = keys[i - 1]
			local span = b[1] - a[1]
			local t = ease(span > 0 and (k - a[1]) / span or 1, b[3])
			return lerpValue(a[2], b[2], t)
		end
	end
	return keys[#keys][2]
end

local function hexColor(h)
	return Color3.fromHex(h)
end

local function evalColor(c, k)
	if type(c) == "string" then
		return hexColor(c)
	end
	if k <= c[1][1] then
		return hexColor(c[1][2])
	end
	for i = 2, #c do
		if k <= c[i][1] then
			local a, b = c[i - 1], c[i]
			local t = (k - a[1]) / math.max(1e-6, b[1] - a[1])
			return hexColor(a[2]):Lerp(hexColor(b[2]), t)
		end
	end
	return hexColor(c[#c][2])
end

-- position of a (possibly moving) attachment at effect time t: at -> move.to with ease and a vertical arc
local function attachPos(L, t)
	local at = L.at or { 0, 0, 0 }
	local m = L.move
	if not m then
		return v3(at)
	end
	local span = m.t1 - m.t0
	local k = math.clamp(span > 0 and (t - m.t0) / span or 1, 0, 1)
	local e = ease(k, m.ease)
	local from = v3(m.from or at)
	local to = v3(m.to)
	local p = from:Lerp(to, e)
	if m.arc then
		p += Vector3.new(0, math.sin(math.pi * e) * m.arc, 0)
	end
	return p
end

local function anglesOf(r)
	if not r then
		return CFrame.identity
	end
	return CFrame.Angles(r[1] * RAD, r[2] * RAD, r[3] * RAD)
end

------------------------------------------------------------------------ property conversion
local function numberSequence(v)
	if type(v) == "number" then
		return NumberSequence.new(v)
	end
	local kps = {}
	local first, last = v[1], v[#v]
	if first[1] > 0 then
		table.insert(kps, NumberSequenceKeypoint.new(0, first[2], first[3] or 0))
	end
	for i, kp in ipairs(v) do
		if i <= 18 then
			table.insert(kps, NumberSequenceKeypoint.new(math.clamp(kp[1], 0, 1), kp[2], kp[3] or 0))
		end
	end
	if last[1] < 1 then
		table.insert(kps, NumberSequenceKeypoint.new(1, last[2], last[3] or 0))
	end
	return NumberSequence.new(kps)
end

local function colorSequence(v)
	if type(v) == "string" then
		return ColorSequence.new(hexColor(v))
	end
	local kps = {}
	if v[1][1] > 0 then
		table.insert(kps, ColorSequenceKeypoint.new(0, hexColor(v[1][2])))
	end
	for _, kp in ipairs(v) do
		table.insert(kps, ColorSequenceKeypoint.new(math.clamp(kp[1], 0, 1), hexColor(kp[2])))
	end
	if v[#v][1] < 1 then
		table.insert(kps, ColorSequenceKeypoint.new(1, hexColor(v[#v][2])))
	end
	return ColorSequence.new(kps)
end

local function numberRange(v)
	if type(v) == "number" then
		return NumberRange.new(v)
	end
	return NumberRange.new(math.min(v[1], v[2]), math.max(v[1], v[2]))
end

local ENUMS = {
	Orientation = Enum.ParticleOrientation,
	EmissionDirection = Enum.NormalId,
	Shape = Enum.ParticleEmitterShape,
	ShapeStyle = Enum.ParticleEmitterShapeStyle,
	ShapeInOut = Enum.ParticleEmitterShapeInOut,
	FlipbookLayout = Enum.ParticleFlipbookLayout,
	FlipbookMode = Enum.ParticleFlipbookMode,
}
local SEQUENCES = { Size = true, Transparency = true, Squash = true }
local RANGES = { Lifetime = true, Speed = true, Rotation = true, RotSpeed = true, FlipbookFramerate = true }

local function applyEmitterProps(pe, props, quality)
	for key, value in pairs(props) do
		if key == "Texture" then
			pe.Texture = Assets.texture(value)
		elseif key == "Color" then
			pe.Color = colorSequence(value)
		elseif SEQUENCES[key] then
			pe[key] = numberSequence(value)
		elseif RANGES[key] then
			pe[key] = numberRange(value)
		elseif key == "SpreadAngle" then
			pe.SpreadAngle = type(value) == "number" and Vector2.new(value, value) or Vector2.new(value[1], value[2])
		elseif key == "Acceleration" then
			pe.Acceleration = v3(value)
		elseif ENUMS[key] then
			pe[key] = ENUMS[key][value]
		else
			pcall(function()
				pe[key] = value
			end)
		end
	end
end

local function anchoredPart(props)
	local p = Instance.new("Part")
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.Locked = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	for k, v in pairs(props or {}) do
		p[k] = v
	end
	return p
end

------------------------------------------------------------------------ playback items
-- Every item has :step(t) (effect time) and :destroy(). Emitters also have :setFrozen(bool).

local function makeEmitter(play, L)
	local item = {}
	local att, holder
	if L.part then
		holder = anchoredPart({ Transparency = 1, Size = v3(L.part), CFrame = play.origin * CFrame.new(attachPos(L, 0)) * anglesOf(L.rot) })
		holder.Parent = play.folder
	else
		att = Instance.new("Attachment")
		att.CFrame = CFrame.new(attachPos(L, 0)) * anglesOf(L.rot)
		att.Parent = play.root
	end
	local pe = Instance.new("ParticleEmitter")
	pe.Rate = 0
	pe.Enabled = true
	applyEmitterProps(pe, L.props, play.quality)
	pe.Parent = att or holder
	local emits = L.emits or {}
	local fired = {}
	function item:step(t)
		local p = attachPos(L, t)
		if att then
			att.Position = p
		else
			holder.CFrame = play.origin * CFrame.new(p) * anglesOf(L.rot)
		end
		for i, em in ipairs(emits) do
			if not fired[i] and t >= em[1] then
				fired[i] = true
				local n = math.max(1, math.floor(em[2] * play.quality + 0.5))
				if em[2] > 0 then
					pe:Emit(n)
				end
			end
		end
		local rate = 0
		for _, w in ipairs(L.rate or {}) do
			if t >= w[1] and t < w[2] then
				rate = w[3] * play.quality
			end
		end
		pe.Rate = rate
	end
	function item:setFrozen(frozen)
		pe.TimeScale = frozen and 0 or 1
	end
	function item:destroy()
		pe.Enabled = false
		if holder then
			holder:Destroy()
		elseif att then
			att:Destroy()
		end
	end
	return item
end

local MATERIALS = {
	Neon = Enum.Material.Neon,
	ForceField = Enum.Material.ForceField,
	Glass = Enum.Material.Glass,
	Ice = Enum.Material.Ice,
	Textured = Enum.Material.SmoothPlastic,
}

-- Part + SpecialMesh shell: scale / transparency / colour / spin keys, optional moving path.
local function makeShell(play, L)
	local item = {}
	local part = anchoredPart({ Material = MATERIALS[L.material or "Neon"] or Enum.Material.Neon, Transparency = 1, Size = Vector3.one })
	local mesh = Instance.new("SpecialMesh")
	mesh.MeshType = Enum.MeshType.FileMesh
	mesh.MeshId = Assets.mesh(L.mesh)
	if L.texture then
		mesh.TextureId = Assets.texture(L.texture)
	end
	mesh.Parent = part
	local base = anglesOf(L.rot)
	local axis = L.spinAxis and v3(L.spinAxis).Unit or Vector3.yAxis
	local meshScale = Assets.meshScale(L.mesh)
	local life = L.life or 0.5
	local t0 = L.t0 or 0
	function item:step(t)
		local age = t - t0
		if age < 0 or age >= life then
			if part.Parent then
				part.Parent = nil
			end
			return
		end
		local k = age / life
		local s = evalKeys(L.scale, k, 1)
		local sv = type(s) == "table" and v3(s) or Vector3.new(s, s, s)
		mesh.Scale = sv * meshScale
		local spin = type(L.spin) == "number" and L.spin * age or evalKeys(L.spin, k, 0)
		local p = attachPos(L, t)
		if L.velocity then
			p += v3(L.velocity) * age
		end
		part.CFrame = play.origin * CFrame.new(p) * base * CFrame.fromAxisAngle(axis, spin * RAD)
		local tr = evalKeys(L.transparency, k, 0)
		part.Transparency = math.clamp(tr, L.texture and 0.02 or 0, 1)
		local c = L.color and evalColor(L.color, k) or Color3.new(1, 1, 1)
		part.Color = c
		if L.texture then
			local b = L.brightness or 1
			mesh.VertexColor = Vector3.new(c.R * b, c.G * b, c.B * b)
		end
		if not part.Parent then
			part.Parent = play.folder
		end
	end
	function item:destroy()
		part:Destroy()
	end
	return item
end

local function makeBeam(play, L)
	local item = {}
	local a0 = Instance.new("Attachment")
	local a1 = Instance.new("Attachment")
	a0.Position = v3(L.from)
	a1.Position = v3(L.from)
	a0.Parent = play.root
	a1.Parent = play.root
	local beam = Instance.new("Beam")
	beam.Attachment0 = a0
	beam.Attachment1 = a1
	beam.Texture = Assets.texture(L.texture)
	beam.TextureMode = Enum.TextureMode.Wrap
	beam.TextureLength = L.textureLength or 8
	beam.TextureSpeed = L.textureSpeed or 0 -- texture lengths per second, same unit the previewer uses
	beam.LightEmission = L.lightEmission or 1
	beam.Brightness = L.brightness or 1
	beam.FaceCamera = true
	beam.Segments = L.segments or 20
	beam.Enabled = false
	beam.Parent = play.root
	local life = L.life or 1
	local t0 = L.t0 or 0
	function item:step(t)
		local age = t - t0
		if age < 0 or age >= life then
			beam.Enabled = false
			return
		end
		local k = age / life
		local from = v3(L.from)
		local to = v3(evalKeys(L.to, k, L.to))
		local reach = evalKeys(L.reach, k, 1)
		a1.Position = from:Lerp(to, reach)
		local w = evalKeys(L.width, k, 1)
		beam.Width0 = type(w) == "table" and w[1] or w
		beam.Width1 = type(w) == "table" and w[2] or w
		beam.Color = ColorSequence.new(evalColor(L.color, k))
		beam.Transparency = NumberSequence.new(math.clamp(evalKeys(L.transparency, k, 0), 0, 1))
		beam.Enabled = true
	end
	function item:destroy()
		beam:Destroy()
		a0:Destroy()
		a1:Destroy()
	end
	return item
end

-- Neon zig-zag lightning made of thin parts, rebuilt every `flicker` seconds.
local function makeBolt(play, L)
	local item = {}
	local parts = {}
	local key = -1
	local rng = Random.new(L.seed or 7)
	local function clear()
		for _, p in ipairs(parts) do
			p:Destroy()
		end
		table.clear(parts)
	end
	local function segment(a, b, thick, color)
		local p = anchoredPart({ Material = Enum.Material.Neon, Color = color, Size = Vector3.new(thick, thick, (b - a).Magnitude) })
		p.CFrame = CFrame.lookAt((a + b) / 2, b)
		p.Parent = play.folder
		table.insert(parts, p)
	end
	local function build()
		clear()
		local a = play.origin * v3(L.from)
		local b = play.origin * v3(L.to)
		local d = b - a
		local side = d:Cross(Vector3.new(0, 1, 0.01)).Unit
		local up = side:Cross(d).Unit
		local n = L.segments or 8
		local jit = L.jitter or 1.2
		local pts = { a }
		for i = 1, n - 1 do
			table.insert(pts, a + d * (i / n) + side * rng:NextNumber(-jit, jit) + up * rng:NextNumber(-jit, jit))
		end
		table.insert(pts, b)
		local col = hexColor(L.color or "#ffffff")
		local th = L.thickness or 0.35
		for i = 1, #pts - 1 do
			segment(pts[i], pts[i + 1], th, col)
			segment(pts[i], pts[i + 1], th * 0.4, Color3.new(1, 1, 1))
		end
	end
	function item:step(t)
		local age = t - (L.t0 or 0)
		local life = L.life or 0.3
		if age < 0 or age >= life then
			if #parts > 0 then
				clear()
			end
			return
		end
		local k = math.floor(age / (L.flicker or 0.05))
		if k ~= key then
			key = k
			build()
		end
		local tr = evalKeys(L.transparency, age / life, 0)
		for _, p in ipairs(parts) do
			p.Transparency = tr
		end
	end
	function item:destroy()
		clear()
	end
	return item
end

-- Ground debris: "crater" = slabs that pop up in a ring around a dark pit (they take the ground's material
-- and colour); "fling" = chunks thrown on ballistic arcs (computed, not physics, so it's identical everywhere).
local function makeDebris(play, D)
	local item = {}
	local rng = Random.new(D.seed or 11)
	local center = play.origin * v3(D.at or { 0, 0, 0 })
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { play.folder, play.caster }
	local hit = Workspace:Raycast(center + Vector3.new(0, 8, 0), Vector3.new(0, -30, 0), params)
	local groundY = hit and hit.Position.Y or center.Y
	local material = hit and hit.Material or Enum.Material.Sand
	local color = hit and hit.Instance and hit.Instance:IsA("BasePart") and hit.Instance.Color or Color3.fromRGB(220, 199, 157)
	if D.color then
		color = hexColor(D.color)
	end
	local n = D.count or 12
	local R = D.radius or 6
	local s = D.size or 2
	local chunks = {}
	for i = 1, n do
		local a = (i / n) * math.pi * 2 + rng:NextNumber(-0.2, 0.2)
		local c = {
			a = a,
			size = Vector3.new(s * rng:NextNumber(0.7, 1.5), s * rng:NextNumber(0.25, 0.6), s * rng:NextNumber(0.6, 1.3)),
			r = R * rng:NextNumber(0.85, 1.15),
			tilt = rng:NextNumber(20, 55),
			spin = rng:NextNumber(-15, 15),
			up = (D.speed or 30) * rng:NextNumber(0.6, 1.2),
			out = (D.speed or 30) * 0.35 * rng:NextNumber(0.5, 1.5),
			rs = Vector3.new(rng:NextNumber(-12, 12), rng:NextNumber(-12, 12), rng:NextNumber(-12, 12)),
		}
		c.part = anchoredPart({ Material = material, Color = color:Lerp(Color3.new(0, 0, 0), rng:NextNumber(0, 0.12)), Size = c.size })
		table.insert(chunks, c)
	end
	local pit
	if D.kind == "crater" then
		pit = anchoredPart({ Shape = Enum.PartType.Cylinder, Material = Enum.Material.SmoothPlastic, Color = hexColor(D.pitColor or "#2a2420"), Size = Vector3.new(0.1, 1, 1) })
	end
	local life = D.life or 3
	function item:step(t)
		local age = t - D.t
		local visible = age >= 0 and age <= life
		for _, c in ipairs(chunks) do
			c.part.Parent = visible and play.folder or nil
		end
		if pit then
			pit.Parent = visible and play.folder or nil
		end
		if not visible then
			return
		end
		local sink = math.max(0, (age - (life - 0.6)) / 0.6)
		if pit then
			local k = math.min(1, age / 0.08)
			local d = R * 1.9 * k
			pit.Size = Vector3.new(0.1, math.max(0.1, d), math.max(0.1, d))
			pit.CFrame = CFrame.new(center.X, groundY + 0.05, center.Z) * CFrame.Angles(0, 0, math.pi / 2)
			pit.Transparency = sink
		end
		for _, c in ipairs(chunks) do
			if D.kind == "crater" then
				local e = ease(math.min(1, age / 0.1), "outBack")
				c.part.Size = c.size * math.max(0.05, e)
				local pos = Vector3.new(center.X + math.cos(c.a) * c.r, groundY + c.size.Y * 0.25 - sink * 2, center.Z + math.sin(c.a) * c.r)
				c.part.CFrame = CFrame.new(pos) * CFrame.Angles(0, -c.a, 0) * CFrame.Angles(0, 0, c.tilt * RAD) * CFrame.Angles(0, c.spin * RAD, 0)
			else
				local tt = math.min(age, 1.6)
				local y = groundY + 0.5 + c.up * tt - 35 * tt * tt
				local k = math.clamp(1 - (age - life + 0.5) / 0.5, 0, 1)
				c.part.Size = Vector3.one * math.max(0.05, c.size.X * 0.45 * k)
				local pos = Vector3.new(center.X + math.cos(c.a) * c.out * tt, math.max(groundY + 0.3, y), center.Z + math.sin(c.a) * c.out * tt)
				c.part.CFrame = CFrame.new(pos) * CFrame.Angles(c.rs.X * tt, c.rs.Y * tt, c.rs.Z * tt)
			end
		end
	end
	function item:destroy()
		for _, c in ipairs(chunks) do
			c.part:Destroy()
		end
		if pit then
			pit:Destroy()
		end
	end
	return item
end

local function makeLight(play, Lt)
	local item = {}
	local att = Instance.new("Attachment")
	att.Position = attachPos(Lt, 0)
	att.Parent = play.root
	local light = Instance.new("PointLight")
	light.Color = hexColor(Lt.color or "#ffffff")
	light.Range = math.min(60, Lt.range or 16)
	light.Brightness = 0
	light.Shadows = false
	light.Parent = att
	local keys = Lt.brightness
	function item:step(t)
		att.Position = attachPos(Lt, t)
		light.Brightness = (t < keys[1][1]) and 0 or math.max(0, evalKeys(keys, t, 0))
	end
	function item:destroy()
		att:Destroy()
	end
	return item
end

-- Damage number: pops (squash -> stretch -> settle), arcs up and away under gravity, fades.
local function makeNumber(play, N)
	local item = {}
	local att = Instance.new("Attachment")
	att.Position = v3(N.at)
	att.Parent = play.root
	local gui = Instance.new("BillboardGui")
	gui.AlwaysOnTop = true
	gui.LightInfluence = 0
	gui.Size = UDim2.fromScale(6, 3)
	gui.Enabled = false
	gui.Parent = att
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.Size = UDim2.fromScale(1, 1)
	label.AnchorPoint = Vector2.new(0.5, 0.5)
	label.Position = UDim2.fromScale(0.5, 0.5)
	label.Font = Enum.Font.LuckiestGuy
	label.TextScaled = true
	label.Text = N.text
	label.TextColor3 = hexColor(N.color or "#ffd23a")
	label.TextStrokeColor3 = Color3.fromRGB(20, 10, 6)
	label.TextStrokeTransparency = 0
	label.Parent = gui
	local life = N.life or 1.25
	local vel = N.vel and v3(N.vel) or Vector3.new(2.5, 17, 0)
	local size = N.size or 2.6
	local pop = { { 0, { 0.2, 0.2, 0 } }, { 0.06, { 1.5, 0.7, 0 }, "out" }, { 0.14, { 0.85, 1.25, 0 } }, { 0.24, { 1, 1, 0 } } }
	function item:step(t)
		local age = t - N.t
		if age < 0 or age > life then
			gui.Enabled = false
			return
		end
		att.Position = v3(N.at) + vel * age - Vector3.new(0, 15 * age * age, 0)
		local p = evalKeys(pop, age, { 1, 1, 0 })
		gui.Size = UDim2.fromScale(size * 2 * p[1], size * p[2])
		local fade = age > life - 0.25 and (age - (life - 0.25)) / 0.25 or 0
		label.TextTransparency = fade
		label.TextStrokeTransparency = fade
		gui.Enabled = true
	end
	function item:destroy()
		att:Destroy()
	end
	return item
end

-- Afterimage: a flat-colour clone of the caster's body left at a point on a dash path.
local function makeGhost(play, G)
	local item = {}
	local model
	local life = G.life or 0.35
	local function build()
		local caster = play.caster
		if not caster then
			return
		end
		local root = caster:FindFirstChild("HumanoidRootPart")
		if not root then
			return
		end
		model = Instance.new("Model")
		-- spec positions are at the feet; rebuild the body from each part's offset to the root part
		local feetToRoot = CFrame.new(0, AnimeVFX.HipOffset(caster), 0)
		local place = play.origin * CFrame.new(v3(G.at)) * feetToRoot
		for _, d in ipairs(caster:GetDescendants()) do
			if d:IsA("BasePart") and d.Transparency < 1 and d ~= root then
				local p = anchoredPart({ Material = Enum.Material.Neon, Color = hexColor(G.color or "#ffffff"), Size = d.Size, Transparency = 0.45 })
				p.CFrame = place * root.CFrame:ToObjectSpace(d.CFrame)
				if d:IsA("MeshPart") then
					local sm = Instance.new("SpecialMesh")
					sm.MeshType = Enum.MeshType.FileMesh
					sm.MeshId = d.MeshId
					sm.Scale = d.Size / d.MeshSize
					sm.Parent = p
				end
				p.Parent = model
			end
		end
		model.Parent = play.folder
	end
	function item:step(t)
		local age = t - G.t
		if age < 0 then
			return
		end
		if age >= life then
			if model then
				model:Destroy()
				model = nil
			end
			return
		end
		if not model then
			build()
		end
		if model then
			for _, p in ipairs(model:GetChildren()) do
				p.Transparency = 0.45 + 0.55 * (age / life)
			end
		end
	end
	function item:destroy()
		if model then
			model:Destroy()
		end
	end
	return item
end

------------------------------------------------------------------------ camera + screen
local shakers = {}
local shakeBound = false
local function bindShake()
	if shakeBound then
		return
	end
	shakeBound = true
	RunService:BindToRenderStep("AnimeVFXShake", Enum.RenderPriority.Camera.Value + 1, function()
		local now = os.clock()
		local off = Vector3.zero
		for i = #shakers, 1, -1 do
			local s = shakers[i]
			local k = (now - s.start) / s.dur
			if k >= 1 then
				table.remove(shakers, i)
			else
				local amp = s.amp * (1 - k) ^ 2
				local w = (now - s.start) * s.freq
				off += Vector3.new(math.sin(w * 6.1 + 1.3), math.sin(w * 7.3 + 4.1) * 0.8, math.sin(w * 5.2 + 2.2) * 0.5) * amp
			end
		end
		if off.Magnitude > 0 then
			local cam = Workspace.CurrentCamera
			cam.CFrame = cam.CFrame * CFrame.new(off * 0.35) * CFrame.Angles(off.Y * 0.01, off.X * 0.01, 0)
		end
	end)
end

function AnimeVFX.Shake(amp, dur, freq, worldPos)
	local scale = 1
	if worldPos then
		local cam = Workspace.CurrentCamera
		local dist = (cam.CFrame.Position - worldPos).Magnitude
		scale = math.clamp(1 - (dist - 25) / 120, 0, 1)
	end
	if scale <= 0 then
		return
	end
	bindShake()
	table.insert(shakers, { start = os.clock(), amp = amp * scale, dur = dur, freq = freq or 22 })
end

local function getGrade()
	local cc = Lighting:FindFirstChild("AnimeVFX_Grade")
	if not cc then
		cc = Instance.new("ColorCorrectionEffect")
		cc.Name = "AnimeVFX_Grade"
		cc.Parent = Lighting
	end
	return cc
end

-- Impact frames. Roblox can't invert the screen, so "invert" paints the world white with characters as black
-- silhouettes (ColorCorrection + Highlight), "mono" the reverse, "white" a hot flash.
local impactHighlights = {}
local function setImpact(play, mode)
	local cc = getGrade()
	for _, h in ipairs(impactHighlights) do
		h:Destroy()
	end
	table.clear(impactHighlights)
	if not mode then
		return false
	end
	local fill
	if mode == "invert" then
		cc.Brightness, cc.Contrast, cc.Saturation = 0.75, 1, -1
		fill = Color3.new(0, 0, 0)
	elseif mode == "mono" then
		cc.Brightness, cc.Contrast, cc.Saturation = -0.7, 1, -1
		fill = Color3.new(1, 1, 1)
	elseif mode == "white" then
		cc.Brightness, cc.Contrast, cc.Saturation = 0.35, 0.2, -0.6
	elseif mode == "black" then
		cc.Brightness, cc.Contrast, cc.Saturation = -0.35, 0.6, -1
	end
	if fill then
		local models = {}
		if play.caster then
			table.insert(models, play.caster)
		end
		for _, m in ipairs(play.targets) do
			table.insert(models, m)
		end
		for _, m in ipairs(models) do
			if m then
				local h = Instance.new("Highlight")
				h.FillColor = fill
				h.FillTransparency = 0
				h.OutlineTransparency = 1
				h.DepthMode = Enum.HighlightDepthMode.AlwaysOnTop
				h.Adornee = m
				h.Parent = play.folder
				table.insert(impactHighlights, h)
			end
		end
	end
	return true
end

------------------------------------------------------------------------ hit-stop helpers
local function animator(model)
	local hum = model and model:FindFirstChildOfClass("Humanoid")
	return hum and hum:FindFirstChildOfClass("Animator")
end

local function freezeAnimations(models, frozen, saved)
	for _, m in ipairs(models) do
		local an = animator(m)
		if an then
			for _, track in ipairs(an:GetPlayingAnimationTracks()) do
				if frozen then
					saved[track] = track.Speed
					track:AdjustSpeed(0)
				elseif saved[track] then
					track:AdjustSpeed(saved[track])
					saved[track] = nil
				end
			end
		end
	end
end

------------------------------------------------------------------------ public API
-- Height from the feet to the HumanoidRootPart centre (specs are authored with the feet at the origin).
function AnimeVFX.HipOffset(character)
	local hum = character and character:FindFirstChildOfClass("Humanoid")
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if hum and root then
		return hum.HipHeight + root.Size.Y / 2
	end
	return 3
end

-- The CFrame to cast from: the caster's feet, facing where the root part faces (flattened to the ground).
function AnimeVFX.CastFrame(character)
	local root = character:FindFirstChild("HumanoidRootPart")
	local look = root.CFrame.LookVector * Vector3.new(1, 0, 1)
	if look.Magnitude < 1e-3 then
		look = Vector3.new(0, 0, -1)
	end
	local feet = root.Position - Vector3.new(0, AnimeVFX.HipOffset(character), 0)
	return CFrame.lookAt(feet, feet + look.Unit)
end

function AnimeVFX.Get(name)
	local effects = script:WaitForChild("Effects")
	local mod = effects:FindFirstChild(name)
	assert(mod, "AnimeVFX: unknown effect " .. tostring(name))
	return require(mod)
end

--[[ Play(effect, originCFrame, opts)
	effect: name (string) or spec table
	opts.caster   Model of the caster (afterimages, impact silhouettes, paused animations during hit-stop)
	opts.targets  { Model } hit targets (impact silhouettes, white hit flash, paused animations)
	opts.onHit    function(hitIndex, effectTime) called at each spec.hits entry (apply knockback / play a
	              hit-reaction animation here: squash & stretch on the target belongs in that animation)
	opts.camera   false to skip shakes, grade and impact frames (for effects far from the local player)
	Returns a handle with :Stop().
]]
function AnimeVFX.Play(effect, origin, opts)
	opts = opts or {}
	local spec = type(effect) == "string" and AnimeVFX.Get(effect) or effect
	local play = {
		spec = spec,
		origin = origin,
		caster = opts.caster,
		targets = opts.targets or {},
		quality = math.clamp(AnimeVFX.Quality * autoQuality(), 0.3, 1),
		folder = Instance.new("Folder"),
	}
	play.folder.Name = spec.name or "AnimeVFX"
	play.folder.Parent = folder()
	play.root = anchoredPart({ Transparency = 1, Size = Vector3.new(0.2, 0.2, 0.2), CFrame = origin })
	play.root.Name = "Root"
	play.root.Parent = play.folder

	local items, emitters = {}, {}
	for _, L in ipairs(spec.layers or {}) do
		local it
		if L.type == "emitter" then
			it = makeEmitter(play, L)
			table.insert(emitters, it)
		elseif L.type == "shell" then
			it = makeShell(play, L)
		elseif L.type == "beam" then
			it = makeBeam(play, L)
		elseif L.type == "bolt" then
			it = makeBolt(play, L)
		end
		if it then
			table.insert(items, it)
		end
	end
	for _, D in ipairs(spec.debris or {}) do
		table.insert(items, makeDebris(play, D))
	end
	for _, Lt in ipairs(spec.lights or {}) do
		table.insert(items, makeLight(play, Lt))
	end
	for _, N in ipairs(spec.numbers or {}) do
		table.insert(items, makeNumber(play, N))
	end
	for _, G in ipairs(spec.ghosts or {}) do
		table.insert(items, makeGhost(play, G))
	end

	local useCamera = opts.camera ~= false
	local stops = table.clone(spec.hitstop or {})
	table.sort(stops, function(a, b)
		return a.t < b.t
	end)
	local shakes = table.clone(spec.shakes or {})
	local impacts = spec.impact or {}
	local hits = spec.hits or {}
	local grade = spec.grade
	local total = (spec.duration or 2) + 0.2
	for _, h in ipairs(stops) do
		total += h.dur
	end

	local te, real, stopIndex, frozenUntil = 0, 0, 1, nil
	local savedTracks = {}
	local shakeFired, hitFired = {}, {}
	local impactActive = false
	local conn
	local handle = {}

	local function setFrozen(frozen)
		for _, e in ipairs(emitters) do
			e:setFrozen(frozen)
		end
		local models = { play.caster }
		for _, m in ipairs(play.targets) do
			table.insert(models, m)
		end
		freezeAnimations(models, frozen, savedTracks)
	end

	local function finish()
		if conn then
			conn:Disconnect()
			conn = nil
		end
		if frozenUntil then
			setFrozen(false)
		end
		if impactActive then
			setImpact(play, nil)
		end
		local cc = Lighting:FindFirstChild("AnimeVFX_Grade")
		if cc and grade then
			cc.Brightness, cc.Contrast, cc.Saturation, cc.TintColor = 0, 0, 0, Color3.new(1, 1, 1)
		end
		for _, it in ipairs(items) do
			it:destroy()
		end
		task.delay(3, function()
			play.folder:Destroy()
		end)
	end

	conn = RunService.Heartbeat:Connect(function(dt)
		real += dt
		-- hit-stop: hold effect time, freeze emitters and animations, keep shaking
		if frozenUntil then
			if real >= frozenUntil then
				frozenUntil = nil
				setFrozen(false)
			end
		else
			local nextStop = stops[stopIndex]
			local newTe = te + dt
			if nextStop and newTe >= nextStop.t then
				te = nextStop.t
				frozenUntil = real + nextStop.dur
				stopIndex += 1
				setFrozen(true)
			else
				te = newTe
			end
		end
		for _, it in ipairs(items) do
			it:step(te)
		end
		for i, h in ipairs(hits) do
			if not hitFired[i] and te >= h.t then
				hitFired[i] = true
				for _, m in ipairs(play.targets) do
					local hl = Instance.new("Highlight") -- white hit flash
					hl.FillColor = Color3.new(1, 1, 1)
					hl.FillTransparency = 0.2
					hl.OutlineTransparency = 1
					hl.Adornee = m
					hl.Parent = play.folder
					task.delay(0.08, function()
						hl:Destroy()
					end)
				end
				if opts.onHit then
					task.spawn(opts.onHit, i, te)
				end
			end
		end
		if useCamera then
			for i, s in ipairs(shakes) do
				if not shakeFired[i] and te >= s.t then
					shakeFired[i] = true
					AnimeVFX.Shake(s.amp, s.dur, s.freq, origin.Position)
				end
			end
			local mode
			for _, f in ipairs(impacts) do
				if te >= f.t and te < f.t + f.dur + (frozenUntil and 0.06 or 0) then
					mode = f.mode
				end
			end
			if mode then
				impactActive = setImpact(play, mode)
			elseif impactActive then
				impactActive = setImpact(play, nil)
			end
			if grade and #grade > 0 and not mode then
				local cc = getGrade()
				local a, b, k = grade[1], grade[1], 0
				for j = 2, #grade do
					if te <= grade[j][1] then
						a, b = grade[j - 1], grade[j]
						k = (te - a[1]) / math.max(1e-6, b[1] - a[1])
						break
					end
					a, b = grade[j], grade[j]
				end
				cc.Brightness = lerp(a[2], b[2], k)
				cc.Contrast = lerp(a[3], b[3], k)
				cc.Saturation = lerp(a[4], b[4], k)
				cc.TintColor = hexColor(a[5] or "#ffffff"):Lerp(hexColor(b[5] or "#ffffff"), k)
			end
		end
		if real >= total then
			finish()
		end
	end)

	function handle:Stop()
		finish()
	end
	handle.Spec = spec
	return handle
end

return AnimeVFX
