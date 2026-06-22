# Luau, Studio architecture, and UI

## Luau

Luau is Roblox's typed dialect of Lua 5.1. Key practices:

- Put `--!strict` at the top of files for type checking; annotate function
  signatures and define `type`/`export type` for shared shapes.
- Use the `task` library, **not** the legacy globals. `task.wait()` is "an
  optimized version of `wait()` that schedules the current thread to resume after
  some time elapses without throttling"; `task.spawn` resumes a function
  immediately on the scheduler, `task.defer` on the next resumption point.
  Legacy `wait()/spawn()/delay()` are "less optimized and configurable."
  [scheduler](https://create.roblox.com/docs/scripting/scheduler)
- Luau has `continue`, compound assignment (`+=`), string interpolation
  (`` `{x}` ``), and generalized iteration (`for k, v in t do`).

## The DataModel: services and script types

UI/code live in services under the DataModel (`game`):

- **ReplicatedStorage** — shared modules/assets visible to server *and* client.
  Put shared `ModuleScript`s and `RemoteEvent`/`RemoteFunction` here.
- **ServerScriptService** — server-only `Script`s and modules. Authoritative
  logic and secrets live here; it does **not** replicate to clients.
- **StarterPlayer.StarterPlayerScripts** — `LocalScript`s that run once per
  player (client controllers).
- **StarterPlayer.StarterCharacterScripts** — scripts copied into the character
  on each spawn.
- **StarterGui** — `ScreenGui`s cloned into each player's **PlayerGui** on join.
- **Workspace** — the 3D world.

Script kinds:

- `Script` — runs on the server (or as specified by `RunContext`).
- `LocalScript` — runs on the client (in PlayerGui, StarterPlayerScripts, the
  character, etc.).
- `ModuleScript` — reusable library `require`d by either side. Rojo file
  conventions: `Name.luau` = ModuleScript, `Name.server.luau` = Script,
  `Name.client.luau` = LocalScript, `init.luau` makes a folder a module.

## Client–server model and remotes

The server is the **single source of truth**. Clients are trusted only to report
their own input. RemoteEvents/RemoteFunctions cross the boundary:

- Create remotes on the server (e.g. in a shared module) and `WaitForChild` them
  on the client.
- `OnServerEvent`'s **first argument is always the `Player`** (engine-injected,
  unspoofable); every argument after it is untrusted client input.
- See `04` for the full anti-exploit pattern (validate → whitelist → authority →
  rate-limit). [security](https://create.roblox.com/docs/scripting/security/security-tactics)

## Characters

- A `Humanoid` gives a model character functionality; the model needs a
  `HumanoidRootPart` and a `Head`. `Humanoid.Died` fires at 0 health;
  `WalkSpeed` defaults to 16.
  [Humanoid](https://create.roblox.com/docs/reference/engine/classes/Humanoid)
- `Players.PlayerAdded` → joining `Player`; `Player.CharacterAdded` → spawned
  character. Safe idiom: `local char = player.Character or player.CharacterAdded:Wait()`.
- `Players.CharacterAutoLoads` defaults `true`; `Players.RespawnTime` defaults
  `5.0`s. Use `Player:LoadCharacterAsync()` for custom spawn flows.
  [players](https://create.roblox.com/docs/players)
- R6 = 6 parts, R15 = 15 parts (richer animation); set in Studio Avatar settings.

## UI/UX (all client-side)

A `ScreenGui` placed in StarterGui clones into each player's `PlayerGui` on
spawn; UI is read/changed on the client.
[containers](https://create.roblox.com/docs/ui/on-screen-containers)

- **Position/size with `UDim2`**: `UDim2.new(xScale, xOffset, yScale, yOffset)`.
  **Scale is resolution-independent** — prefer it over Offset so UI adapts across
  phone/tablet/PC. **AnchorPoint** sets the origin (`(0.5,0.5)` centers).
  [position-and-size](https://create.roblox.com/docs/ui/position-and-size)
- **Layout**: `UIListLayout` (rows/columns, `Padding`, `SortOrder`),
  `UIGridLayout` (uniform cells), `UIPadding`, `UICorner`,
  `UIAspectRatioConstraint` (lock ratio), `UISizeConstraint`,
  `UITextSizeConstraint`, `UIScale`.
- **Mobile-first** (most sessions are mobile): use Scale, keep large tap targets,
  keep controls clear of the bottom-left thumbstick / bottom-right jump button
  and device cutouts; respect `GuiService:GetGuiInset()` and `ScreenInsets`. Use
  `TextScaled` with a `UITextSizeConstraint` for readable text.
  [cross-platform](https://create.roblox.com/docs/projects/cross-platform)
- **Engagement principles** (official): *hierarchy of information* (most
  important first), *feedback* (confirm actions — tween buttons on hover/press),
  readable contrast, vibrant color for the important thing, avoid clutter.
  [ui-ux-design](https://create.roblox.com/docs/production/game-design/ui-ux-design)
- **Frameworks**: Roact is deprecated; **React-lua** is the supported successor;
  **Fusion** and **Vide** are popular reactive options. Plain
  `Instance.new`-constructed UI from client modules is perfectly fine for an MVP
  and needs no extra dependency.

### Minimal patterns

```lua
-- Centered responsive frame with a juicy button (LocalScript)
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local pg = Players.LocalPlayer:WaitForChild("PlayerGui")

local gui = Instance.new("ScreenGui")
gui.ResetOnSpawn = false
gui.Parent = pg

local frame = Instance.new("Frame")
frame.Size = UDim2.fromScale(0.4, 0.3)
frame.Position = UDim2.fromScale(0.5, 0.5)
frame.AnchorPoint = Vector2.new(0.5, 0.5)
frame.Parent = gui
Instance.new("UICorner").Parent = frame

local btn = Instance.new("TextButton")
btn.Size = UDim2.fromScale(0.6, 0.2)
btn.AnchorPoint = Vector2.new(0.5, 0.5)
btn.Position = UDim2.fromScale(0.5, 0.5)
btn.Text = "Play"
btn.TextScaled = true
btn.Parent = frame
local scale = Instance.new("UIScale"); scale.Parent = btn
local quick = TweenInfo.new(0.12)
btn.MouseEnter:Connect(function() TweenService:Create(scale, quick, {Scale = 1.08}):Play() end)
btn.MouseLeave:Connect(function() TweenService:Create(scale, quick, {Scale = 1}):Play() end)
btn.Activated:Connect(function() print("clicked") end)
```
