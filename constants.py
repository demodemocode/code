import os

CODI_VERSION = "0.1.9"

AI_API_KEY = os.getenv("AI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "llama-3.1-sonar-small-128k")  # default fallback model
AI_URL = os.getenv("AI_URL", "https://api.perplexity.ai/chat/completions")  # default provider URL


SKIP_DIRS = {
    # Codi
    ".codi",

    # Node / framework
    "node_modules", ".next", ".turbo",

    # Build / dist
    "dist", "build", "out",

    # Env / project metadata
    ".git", ".husky", ".github",
    ".vscode", ".idea",

    # Cache
    ".cache", ".vercel", "__pycache__",

    # Public assets (no source code)
    "public", "assets",
}

SKIP_FILES = {
    # Package managers
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",

    # Environment files
    ".env", ".env.local", ".env.production", ".env.development",

    # Next.js config
    "next.config.js", "next.config.mjs", "next.config.ts",  "next-env.d.ts",

    # Build config
    "tailwind.config.js", "postcss.config.js",
    "tsconfig.json", "jsconfig.json",

    # README
    "README.md",
}

