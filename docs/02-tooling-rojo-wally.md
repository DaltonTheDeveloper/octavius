# Professional tooling: Rojo, Wally, Selene, StyLua, TestEZ

Serious Roblox development happens in external editors with a git workflow, not
only inside Studio. The standard stack:

## Rojo — filesystem ⇄ Studio sync

[Rojo](https://rojo.space) maps a folder of `.luau` files into the Roblox
DataModel, so you can edit code in VS Code, version it in git, and sync into
Studio live. A project is described by `default.project.json`:

```json
{
  "name": "MyGame",
  "tree": {
    "$className": "DataModel",
    "ReplicatedStorage": { "Shared": { "$path": "src/shared" } },
    "ServerScriptService": { "Server": { "$path": "src/server" } },
    "StarterPlayer": {
      "StarterPlayerScripts": { "Client": { "$path": "src/client" } }
    },
    "Workspace": { "$properties": { "FilteringEnabled": true } }
  }
}
```

Workflow:

```sh
rojo serve                 # then connect via the Rojo Studio plugin (live sync)
rojo build -o MyGame.rbxlx # build a place file (for Open Cloud publishing)
```

File → instance conventions: `Name.luau` → ModuleScript, `Name.server.luau` →
Script, `Name.client.luau` → LocalScript, `init.luau` turns a folder into a
ModuleScript with children. RobloxForge emits exactly this layout
(`src/shared`, `src/server`, `src/client`).

## rokit — toolchain manager

[rokit](https://github.com/rojo-rbx/rokit) (the modern aftman successor) pins
tool versions so everyone/CI uses the same Rojo/Selene/StyLua. RobloxForge writes
a `rokit.toml`; run `rokit install` to fetch the pinned tools.

## Wally — package manager

[Wally](https://wally.run) installs community Luau packages into `Packages/`.
A `wally.toml` lists dependencies (e.g. a data library); `wally install` fetches
them. Example dependency line: `ProfileStore = "loleris/profilestore@1.0.0"`.

## Selene — linter, StyLua — formatter

- **Selene** statically lints Luau; configure with `selene.toml` (`std = "roblox"`).
  Run `selene src`.
- **StyLua** formats Luau deterministically. Run `stylua src`. Wire both into CI
  and a pre-commit hook.

## TestEZ — unit testing

[TestEZ](https://github.com/Roblox/testez) is Roblox's BDD test framework. Write
`*.spec.luau` ModuleScripts that return a function; a runner executes them in
Studio (via the Run command) or headlessly with [run-in-roblox]/Lune in CI.

```lua
-- src/shared/Economy.spec.luau
return function()
    local Economy = require(script.Parent.Economy)
    describe("Economy.price", function()
        it("applies a multiplier", function()
            expect(Economy.price(100, 2)).to.equal(200)
        end)
        it("never goes negative", function()
            expect(Economy.price(-5, 1)).to.equal(0)
        end)
    end)
end
```

Test the **pure/server logic** (economy math, progression, validation helpers) —
the parts that don't need a live DataModel. [Jest-Lua](https://github.com/jsdotlua/jest-lua)
is a modern alternative with a Jest-like API.

## A sane CI loop

```sh
rokit install
selene src
stylua --check src
# run TestEZ specs via run-in-roblox / Lune
rojo build -o game.rbxlx
```
