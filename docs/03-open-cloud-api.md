# Roblox Open Cloud API

Open Cloud lets you manage a live experience programmatically — publish place
updates, read/write DataStores, broadcast to running servers, upload assets, and
read user/group info. This is how automation reaches *past* "opens in Studio".

- **Base host:** `https://apis.roblox.com`
- **Auth:** `x-api-key: <KEY>` header (or OAuth `Authorization: Bearer` for
  third-party apps). Create keys at
  <https://create.roblox.com/dashboard/credentials> — pick the API systems +
  operations, optionally restrict to specific experiences and IPs.
  [api-keys](https://create.roblox.com/docs/cloud/auth/api-keys)
- **v2 resource model:** `https://apis.roblox.com/cloud/v2/...` (hierarchical
  paths, `maxPageSize`/`pageToken` pagination, `updateMask` on writes, error
  shape `{"code","message","details"}`).
  [patterns](https://create.roblox.com/docs/cloud/reference/patterns)

`robloxforge.roblox.opencloud.OpenCloudClient` wraps the endpoints below.

## Publish a place (v1 — the only way to upload place file content)

```
POST https://apis.roblox.com/universes/v1/{universeId}/places/{placeId}/versions?versionType=Published
x-api-key: <KEY>
Content-Type: application/octet-stream   # .rbxl  (use application/xml for .rbxlx)
<binary place file>
-> { "versionNumber": 7 }
```

`versionType=Published` releases to players; `Saved` stores a draft. ~30/min.
The v2 Place resource only manages metadata (`displayName`, `serverSize`, …) — it
cannot upload place content.
[place-publishing](https://create.roblox.com/docs/cloud/open-cloud/usage-place-publishing)

## DataStores (v1)

Base: `https://apis.roblox.com/datastores/v1/universes/{universeId}/standard-datastores`

- Get entry: `GET .../datastore/entries/entry?datastoreName=&entryKey=&scope=global`
- Set entry: `POST` same path with `content-md5` (base64 MD5 of body),
  `content-type: application/json`, optional `roblox-entry-userids` /
  `roblox-entry-attributes` headers; body = JSON value (≤4 MB).
- Increment / Delete / List / Versions endpoints also exist. ~300 req/min per
  universe (read 20 MB/min, write 10 MB/min).
  [datastore reference](https://create.roblox.com/docs/cloud/reference/DataStore)
- **v2** (recommended going forward):
  `.../cloud/v2/universes/{u}/data-stores/{ds}/entries/{id}` with Create/Update
  (`allowMissing`), `etag` optimistic concurrency, attributes/users in the body.

## Messaging service (push to live servers)

```
# v2 (current) — topic in body
POST https://apis.roblox.com/cloud/v2/universes/{universeId}:publishMessage
{ "topic": "your-topic", "message": "Hello" }

# v1 (legacy) — topic in URL
POST https://apis.roblox.com/messaging-service/v1/universes/{universeId}/topics/{topic}
{ "message": "Hello" }
```

Topic ≤80 chars, message ≤1 KiB. Scope `universe-messaging-service:publish`,
~5000/min. In-experience, subscribe with `MessagingService:SubscribeAsync`.
[messaging](https://create.roblox.com/docs/cloud/guides/usage-messaging)

## Assets API (upload images/audio/models)

```
POST https://apis.roblox.com/assets/v1/assets        # multipart/form-data
  request     = {"assetType":"Decal","displayName":"...","description":"...",
                 "creationContext":{"creator":{"userId":"123"}}}   (application/json)
  fileContent = <binary>;type=image/png
-> { "path": "operations/abc", "done": false }        # async Operation
GET  https://apis.roblox.com/assets/v1/operations/{id}  # poll until done -> response.assetId
```

`creator` is exactly one of `userId`/`groupId`. ≤20 MB/file, 1 asset/request;
images ≤8000×8000, audio ≤7 min. Asset uploads, thumbnail generation, and asset
updates are **async Operations** — poll with exponential backoff.
[assets](https://create.roblox.com/docs/cloud/guides/usage-assets)

## Other v2 resources

- **Universe**: `GET/PATCH /cloud/v2/universes/{id}` (visibility, ageRating,
  social links), `:restartServers`, secrets.
- **User**: `GET /cloud/v2/users/{userId}`. **Group**: `GET /cloud/v2/groups/{id}`
  plus `/memberships`, `/roles`, `/join-requests`.
- **Memory stores**, **subscriptions** (monetization), **engine instances**.

## Helper libraries (community — no official SDK)

[rbxcloud](https://github.com/Sleitnick/rbxcloud) (Rust CLI),
[rblx-open-cloud](https://github.com/treeben77/rblx-open-cloud) (Python),
[@relatiocc/opencloud](https://github.com/relatiocc/opencloud) (TypeScript),
[Lune](https://github.com/lune-org/lune) (Luau runtime, reads/writes `.rbxl`).
Roblox publishes an OpenAPI 3 spec for codegen.

> Scope strings appear in dotted (`universe.place:write`) and hyphenated forms;
> v2 reference pages use the dotted form.
