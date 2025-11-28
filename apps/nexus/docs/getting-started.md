# Getting Started with Nexus

Welcome to Nexus! This guide will help you set up and start using your personal knowledge graph portal.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** 18 or higher ([Download](https://nodejs.org/))
- **npm** (comes with Node.js) or **yarn**
- **Git** ([Download](https://git-scm.com/))

Check your versions:
```bash
node --version  # Should be v18.0.0 or higher
npm --version   # Should be 9.0.0 or higher
git --version   # Any recent version
```

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/seb155/Nexus.git
cd Nexus
```

### 2. Install Dependencies

```bash
cd frontend
npm install
```

This will install all necessary packages including:
- React 19
- TypeScript 5.9
- Vite 7
- Tailwind CSS 4
- React Router 7
- Zustand

### 3. Start Development Server

```bash
npm run dev
```

You should see output similar to:
```
VITE v7.2.4  ready in 450 ms

➜  Local:   http://localhost:5173/
➜  Network: http://192.168.1.x:3000/
```

### 4. Open in Browser

Navigate to [http://localhost:5173](http://localhost:5173)

You should see the Nexus dashboard with a VSCode-like interface.

## 🎨 First Steps

### Exploring the Interface

Nexus has a familiar VSCode-inspired layout:

1. **Sidebar (Left)** - Navigation between different sections:
   - 🏠 Dashboard - Overview and quick access
   - 📝 Notes - Rich text editor (coming in Phase 2)
   - ✅ Tasks - Kanban boards (coming in Phase 3)
   - 🗺️ Roadmap - Gantt charts (coming in Phase 4)
   - 🌐 Graph - 3D visualization (coming in Phase 5)
   - ⚙️ Settings - Configuration

2. **Top Bar** - Global actions:
   - Toggle sidebar visibility
   - Switch between light/dark themes
   - User profile (future)

3. **Status Bar (Bottom)** - Current state:
   - Current view
   - Git branch (future)
   - Notifications (future)

### Keyboard Shortcuts

- `Ctrl/Cmd + B` - Toggle sidebar (future)
- `Ctrl/Cmd + Shift + P` - Command palette (future)
- `Ctrl/Cmd + K` - Quick search (future)

## 🛠️ Development

### Project Structure

```
Nexus/
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── layout/    # Layout components (Sidebar, TopBar, etc.)
│   │   │   └── ui/        # Reusable UI components (future)
│   │   ├── pages/         # Route pages
│   │   ├── stores/        # Zustand state management
│   │   ├── lib/           # Utilities
│   │   └── types/         # TypeScript types (future)
│   ├── public/            # Static assets
│   └── package.json       # Dependencies
├── .dev/                  # Development documentation
├── .agent/                # AI workflow documentation
└── docs/                  # User documentation
```

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

### Building for Production

```bash
npm run build
```

This creates an optimized build in `frontend/dist/`:
- Minified JavaScript bundles
- Optimized CSS
- Compressed assets

To preview the production build:
```bash
npm run preview
```

## 🐛 Troubleshooting

### Port Already in Use

If port 3000 is already in use, you can change it in [vite.config.ts](../frontend/vite.config.ts:11):

```typescript
server: {
  port: 3001,  // Change to any available port
  host: '0.0.0.0',
}
```

### Node Version Issues

If you encounter issues, ensure you're using Node.js 18+:

```bash
node --version
```

Consider using [nvm](https://github.com/nvm-sh/nvm) to manage Node versions:

```bash
nvm install 18
nvm use 18
```

### Module Not Found Errors

Try deleting `node_modules` and reinstalling:

```bash
rm -rf node_modules package-lock.json
npm install
```

### Vite Build Errors

Clear Vite cache:

```bash
rm -rf node_modules/.vite
npm run dev
```

## 📚 Next Steps

- Read the [Project Roadmap](../.dev/roadmap/README.md) to see what's coming
- Check [CONTRIBUTING.md](../CONTRIBUTING.md) to learn how to contribute
- Join our discussions on GitHub

## 🙋 Getting Help

- **Documentation:** Browse the [docs](../docs/) folder
- **Issues:** Report bugs on [GitHub Issues](https://github.com/seb155/Nexus/issues)
- **Discussions:** Ask questions on [GitHub Discussions](https://github.com/seb155/Nexus/discussions)

---

**Ready to build your knowledge graph?** 🌐

Navigate to [Dashboard](http://localhost:5173) and start exploring!
