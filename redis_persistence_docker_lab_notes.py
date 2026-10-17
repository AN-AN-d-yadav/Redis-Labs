\
# REDIS PERSISTENCE + DOCKER VOLUME — HANDS-ON LAB NOTES
# ======================================================
#
# Purpose
# -------
# These notes record a hands-on Redis persistence experiment performed with
# Docker. They are intended to be committed to Git as a learning log.
#
# Main lessons:
# 1. Redis serves data primarily from memory (RAM).
# 2. RDB and AOF are Redis persistence mechanisms.
# 3. `docker restart` does NOT delete a container's writable layer.
# 4. Removing a container removes its writable layer.
# 5. A Docker volume can keep Redis persistence files outside the container,
#    allowing a replacement container to reuse those files.
#
# SAFETY NOTE
# -----------
# We used separate disposable containers:
#   - redis-persistence-lab
#   - redis-volume-lab
#
# The existing `pulseboard-redis` container was inspected only. It was not
# reconfigured or removed. Do not run cleanup commands against real project
# containers or volumes unless you are sure what data they contain.
#
#
# 1. REDIS PERSISTENCE: THE BASIC IDEA
# ====================================
#
# Redis stores and serves data primarily from memory. If Redis stops, data
# that exists only in memory can be lost. Persistence means saving data to
# files so Redis can load it again.
#
# RDB SNAPSHOTS
# -------------
# - Redis saves a snapshot of the dataset, commonly in `dump.rdb`.
# - A snapshot represents the dataset at a particular point in time.
# - RDB files are compact and useful for backups.
# - Changes made after the latest snapshot may be lost if Redis stops
#   unexpectedly before another snapshot is saved.
#
# AOF (APPEND ONLY FILE)
# ----------------------
# - Redis records write operations in an append-only persistence log.
# - During startup, Redis can replay recorded operations to rebuild data.
# - Durability depends partly on AOF fsync configuration and whether recent
#   writes have reached storage before a crash or power failure.
# - Depending on Redis version/configuration, AOF files may be organized in
#   `appendonlydir/` with a manifest and base/incremental files.
#
# RDB and AOF can both be enabled. Seeing an RDB file and an AOF directory
# does not by itself prove that a particular key is safely stored in both.
#
#
# 2. INSPECTING THE EXISTING REDIS CONTAINER
# ==========================================
#
# Command:
#   docker exec -it pulseboard-redis redis-cli INFO persistence
#
# Important fields from the observed output:
#
# - `aof_enabled:0`
#   AOF was disabled for this Redis instance at the time of inspection.
#
# - `rdb_last_bgsave_status:ok`
#   The last background RDB save status was successful.
#
# - `rdb_changes_since_last_save:20`
#   Redis reported 20 changes since the last RDB save.
#
# - `rdb_last_load_keys_loaded:1010`
#   During a previous startup/load operation, Redis reported loading 1,010
#   keys.
#
# - `rdb_saves:0`
#   The process's reported counter showed zero RDB save operations during its
#   current process lifetime. This does not mean there cannot be an RDB file.
#
# Important: `aof_enabled:0` means AOF was disabled; it does NOT prove Redis
# had no persistence. RDB and AOF are separate mechanisms.
#
# The existing project Redis container was left untouched.
#
#
# 3. START A DISPOSABLE REDIS CONTAINER WITH AOF
# ==============================================
#
# Command:
#   docker run -d --name redis-persistence-lab -p 6389:6379 redis:7-alpine redis-server --appendonly yes
#
# Options:
# - `docker run`: create and start a container.
# - `-d`: run in detached/background mode.
# - `--name redis-persistence-lab`: assign a recognizable name.
# - `-p 6389:6379`: map host port 6389 to container port 6379.
# - `redis:7-alpine`: use the Redis 7 Alpine image.
# - `redis-server --appendonly yes`: start Redis with AOF enabled.
#
# If host port 6389 is already occupied, choose another available host port.
#
# Check the container:
#   docker ps -a --filter "name=redis-persistence-lab"
#
# A detached `docker run` normally prints a container ID. If no output appears,
# inspect the container with the command above.
#
#
# 4. WRITE AND READ A TEST KEY
# ============================
#
# Write:
#   docker exec -it redis-persistence-lab redis-cli SET lab:message "Redis is working"
#
# Expected response:
#   OK
#
# Read:
#   docker exec -it redis-persistence-lab redis-cli GET lab:message
#
# Expected response:
#   "Redis is working"
#
# This confirms that the key/value can be written and read. By itself, it does
# not yet prove persistence across a restart.
#
#
# 5. TEST A CONTAINER RESTART
# ==========================
#
# Restart:
#   docker restart redis-persistence-lab
#
# Read the key again:
#   docker exec -it redis-persistence-lab redis-cli GET lab:message
#
# Observed result:
#   "Redis is working"
#
# Interpretation:
# The data was available after restart. However, `docker restart` keeps the
# same container and its writable layer. This experiment alone does NOT prove
# that data would survive removing the container and creating a new one.
#
# Redis persistence and Docker storage are different concepts:
# - Redis persistence controls whether/how Redis writes data to files.
# - Docker volumes control whether files in a directory survive container
#   removal and can be reused by another container.
#
#
# 6. INSPECT REDIS PERSISTENCE FILES
# ==================================
#
# Get Redis's configured data directory:
#   docker exec -it redis-persistence-lab redis-cli CONFIG GET dir
#
# Common result:
#   "/data"
#
# List the data directory:
#   docker exec redis-persistence-lab sh -c "ls -la /data"
#
# In this lab, the listing included:
#   appendonlydir/
#   dump.rdb
#
# The `appendonlydir/` folder is associated with AOF files; `dump.rdb` is an
# RDB snapshot file. File presence alone does not prove a particular key is
# safely recorded in both mechanisms.
#
# Inspect the AOF directory:
#   docker exec redis-persistence-lab sh -c "ls -lh /data/appendonlydir"
#
# Exact AOF filenames depend on Redis version and configuration.
#
#
# 7. WHY A DOCKER VOLUME MATTERS
# ==============================
#
# Without a mounted volume, persistence files can live in the container's
# writable layer. Removing the container removes that layer.
#
# A Docker volume is managed separately from a container. If Redis writes its
# persistence files into a directory backed by a volume, a replacement
# container can mount the same volume and reuse those files.
#
# Create a named volume:
#   docker volume create redis-persistence-data
#
# Expected output:
#   redis-persistence-data
#
# Create a new Redis container with that volume mounted at `/data`:
#   docker run -d --name redis-volume-lab -p 6390:6379 -v redis-persistence-data:/data redis:7-alpine redis-server --appendonly yes
#
# Important option:
#   -v redis-persistence-data:/data
#
# `redis-persistence-data` is the Docker volume name; `/data` is the directory
# inside the container. Redis files written under `/data` are stored in the
# mounted volume rather than only in the container's writable layer.
#
#
# 8. WRITE DATA TO THE VOLUME-BACKED REDIS
# ========================================
#
# Write:
#   docker exec -it redis-volume-lab redis-cli SET lab:volume "Survives container replacement"
#
# Expected response:
#   OK
#
# Read:
#   docker exec -it redis-volume-lab redis-cli GET lab:volume
#
# Expected response:
#   "Survives container replacement"
#
#
# 9. REMOVE AND RECREATE THE CONTAINER
# ====================================
#
# Remove only the disposable container:
#   docker rm -f redis-volume-lab
#
# This removes the container, not the separately managed named volume.
#
# Recreate a container with the SAME volume:
#   docker run -d --name redis-volume-lab -p 6390:6379 -v redis-persistence-data:/data redis:7-alpine redis-server --appendonly yes
#
# Read the key:
#   docker exec -it redis-volume-lab redis-cli GET lab:volume
#
# Observed result:
#   "Survives container replacement"
#
# Interpretation:
# The old container was removed and a new container was created. The key was
# still available because Redis loaded persistence data from the same volume.
#
# Caveat: this relies on Redis having successfully written the data to its
# persistence files before the old container was removed. A volume preserves
# files; it does not guarantee every recent write has already been flushed.
#
#
# 10. IMPORTANT DIFFERENCES
# =========================
#
# Action                         Result
# -----------------------------  ---------------------------------------------
# Redis process restart          Redis restarts; persistence may reload data.
# `docker restart <container>`   Same container and writable layer remain.
# Remove container, no volume    Container writable layer is deleted.
# Remove container, same volume  Volume remains and can be mounted by a new
#                                container to reuse saved persistence files.
# Delete the named volume        Volume data is deleted unless another copy
#                                or backup exists.
#
# Remember:
# - Redis persistence is about saving/recovering Redis data.
# - Docker volumes are about keeping files independently of a container.
# - They solve different parts of the durability problem.
#
#
# 11. USEFUL INSPECTION COMMANDS
# ==============================
#
# Check persistence status:
#   docker exec -it redis-volume-lab redis-cli INFO persistence
#
# Check whether AOF is enabled:
#   docker exec -it redis-volume-lab redis-cli CONFIG GET appendonly
#
# Check RDB snapshot settings:
#   docker exec -it redis-volume-lab redis-cli CONFIG GET save
#
# Check Redis data directory:
#   docker exec -it redis-volume-lab redis-cli CONFIG GET dir
#
# List files in the data directory:
#   docker exec redis-volume-lab sh -c "ls -la /data"
#
# List Docker volumes:
#   docker volume ls
#
# Inspect the lab volume:
#   docker volume inspect redis-persistence-data
#
#
# 12. CLEANUP
# ===========
#
# Remove the disposable lab containers when finished:
#   docker rm -f redis-persistence-lab
#   docker rm -f redis-volume-lab
#
# These commands intentionally leave the named volume in place:
#   redis-persistence-data
#
# If you later decide to delete the lab volume too:
#   docker volume rm redis-persistence-data
#
# WARNING: removing the volume deletes the persistence files stored in it.
# Do not remove a volume belonging to a real project unless you intentionally
# want to delete its data.
#
# Do not remove or reconfigure `pulseboard-redis` as part of this lab.
#
#
# 13. WHAT TO REMEMBER FOR REAL PROJECTS
# ======================================
#
# Before using Redis in a Django project:
# - Decide what data is appropriate to cache or store in Redis.
# - Use TTL/expiration for cache entries when suitable.
# - Plan how cached data is invalidated/refreshed after database updates.
# - Decide what the application should do if Redis becomes unavailable.
# - For production, configure persistence and Docker volumes deliberately.
# - Understand backups, monitoring, memory limits, eviction policy, and
#   recovery requirements before relying on Redis for important durable data.
# - Redis persistence is not a substitute for a database backup strategy.
#
# Suggested learning order:
# 1. Redis basics: SET, GET, DEL, EXPIRE, TTL.
# 2. Django integration and caching.
# 3. Cache hit/miss, invalidation, and stale data.
# 4. Redis data structures and use cases.
# 5. Persistence configuration and operational monitoring.
# 6. Replication, Sentinel, and Cluster when your use case requires them.
#
# You do not need to master every persistence implementation detail before
# starting a practical Django integration.
#
#
# LAB SUMMARY
# ===========
#
# In this lab, we:
# - Inspected the existing Redis persistence status without modifying it.
# - Started a separate Redis container with AOF enabled.
# - Wrote/read a key and tested a container restart.
# - Inspected Redis's persistence directory.
# - Created a named Docker volume and mounted it at `/data`.
# - Removed and recreated the disposable volume-backed container.
# - Read the test key successfully after replacement.
#
# Core takeaway:
# Redis persistence determines how Redis saves data to files. Docker volumes
# determine whether those files can outlive a particular container.
