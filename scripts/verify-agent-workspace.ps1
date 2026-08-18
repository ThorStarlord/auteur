# scripts/verify-agent-workspace.ps1
# Verifies repository-workspace invariants before an agent/execution session
# begins. Generic: no repository names, SHAs, or paths are hard-coded.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts/verify-agent-workspace.ps1 `
#     -ExpectedRoot  "H:\path\to\repo" `
#     -ExpectedHead  "<sha or ref>" `
#     -RequireStandalone
#
# Optional:
#   -ExpectedRemoteCount <n>   require this many remotes
#   -RequireNoRemotes          require zero remotes (isolation)
#   -ReportWorkingTree         print a working-tree summary (does not fail on
#                              untracked/modified files)
#
# Exit code 0 = workspace matches. Non-zero with a message = do NOT start the
# session; the intended workspace is not bound.

param(
    [Parameter(Mandatory = $true)]
    [string]$ExpectedRoot,

    [Parameter(Mandatory = $true)]
    [string]$ExpectedHead,

    [switch]$RequireStandalone,

    [int]$ExpectedRemoteCount = -1,

    [switch]$RequireNoRemotes,

    [switch]$ReportWorkingTree
)

$ErrorActionPreference = "Stop"
$failures = New-Object System.Collections.Generic.List[string]

# Normalize a path for comparison: git emits POSIX separators; Windows shells
# (and callers) use backslashes. Comparing the resolved full path is enough.
function Normalize-PathValue {
    param([string]$Path)
    if (-not $Path) { return "" }
    try { return (Resolve-Path $Path -ErrorAction Stop).Path -replace '\\', '/' }
    catch { return $Path -replace '\\', '/' }
}

function Test-Ok {
    param([string]$Name, [bool]$Ok, [string]$Detail)
    if ($Ok) {
        Write-Host ("  {0,-16} OK   {1}" -f $Name, $Detail)
    }
    else {
        Write-Host ("  {0,-16} FAIL {1}" -f $Name, $Detail)
        $script:failures.Add($Name)
    }
}

Write-Host "WORKSPACE PREFLIGHT"
Write-Host "==================="

# 1. Repository root (top-level) must match the expected workspace.
$topLevel = (git rev-parse --show-toplevel 2>$null)
$topLevelNorm = Normalize-PathValue $topLevel
$expectedRootNorm = Normalize-PathValue $ExpectedRoot
Test-Ok "toplevel" ($topLevelNorm -eq $expectedRootNorm) ("expected '{0}'; got '{1}'" -f $ExpectedRoot, $topLevel)

# 2. Standalone vs linked topology.
# A tree that is actually the main checkout of a repository has the same git
# dir and git-common-dir. A linked worktree has its own private git dir under
# <main>/.git/worktrees/<name> that differs from the common dir, so the two
# paths diverge. This is the reliable discriminator; the mere presence of a
# .git/worktrees directory does not imply a linked worktree (git creates it in
# every repository).
$gitDir = (git rev-parse --absolute-git-dir 2>$null)
$commonDir = (git rev-parse --git-common-dir 2>$null)
if (-not [System.IO.Path]::IsPathRooted($commonDir)) {
    $commonDir = Join-Path $topLevel $commonDir
}
$gitDirNorm = Normalize-PathValue $gitDir
$commonDirNorm = Normalize-PathValue $commonDir

# isStandalone: this checkout is the main checkout of its repository (its git
# dir and common dir coincide). A linked worktree splits them.
$isStandalone = ($gitDirNorm -eq $commonDirNorm)
Test-Ok "topology" ($isStandalone -or (-not $RequireStandalone)) `
    ("git-dir='{0}'; common-dir='{1}'; require-standalone={2}; detected={3}" -f $gitDir, $commonDir, $RequireStandalone, ($(if ($isStandalone) {"standalone"} else {"linked"})))

# 3. HEAD must be the expected commit.
$head = (git rev-parse HEAD 2>$null)
Test-Ok "HEAD" ($head -eq $ExpectedHead) ("expected '{0}'; got '{1}'" -f $ExpectedHead, $head)

# 4. Remote policy.
$remotes = @(git remote 2>$null)
$remoteCount = $remotes.Count
if ($RequireNoRemotes) {
    Test-Ok "remotes" ($remoteCount -eq 0) ("expected 0; got {0}" -f $remoteCount)
}
elseif ($ExpectedRemoteCount -ge 0) {
    Test-Ok "remotes" ($remoteCount -eq $ExpectedRemoteCount) ("expected {0}; got {1}" -f $ExpectedRemoteCount, $remoteCount)
}
else {
    Test-Ok "remotes" $true ("{0} present (no policy set)" -f $remoteCount)
}

# 5. Optional: working-tree summary for diagnostics only.
if ($ReportWorkingTree) {
    Write-Host ""
    Write-Host "WORKING-TREE SUMMARY (informational)"
    git status --porcelain
}

Write-Host ""
if ($failures.Count -eq 0) {
    Write-Host "WORKSPACE_OK  - Session may start."
    exit 0
}
else {
    Write-Host ("WORKSPACE_FAIL - {0} check(s) failed:" -f $failures.Count)
    foreach ($f in $failures) { Write-Host ("  - " + $f) }
    Write-Host "Do not start the session. Bind the correct workspace first."
    exit 1
}
