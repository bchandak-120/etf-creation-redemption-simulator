# GitHub Pages Deployment Instructions

## Step 1: Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `portfolio-website`
3. Make it Public
4. Don't initialize with README
5. Click "Create repository"

## Step 2: Connect and Push
Copy these commands and run them in your terminal:

```bash
git remote add origin https://github.com/YOUR_USERNAME/portfolio-website.git
git branch -M main
git push -u origin main
```

## Step 3: Enable GitHub Pages
1. Go to your repository on GitHub
2. Click "Settings" tab
3. Scroll down to "Pages" section
4. Under "Build and deployment", select "Deploy from a branch"
5. Source: "Deploy from a branch"
6. Branch: "main"
7. Folder: "/ (root)"
8. Click "Save"

## Step 4: Get Your Live Link
Your portfolio will be live at:
https://YOUR_USERNAME.github.io/portfolio-website/my-portfolio/

## Alternative: Direct File Access
While setting up GitHub, you can view your portfolio by:
1. Double-click: `portfolio.html`
2. Or open: `index.html` (full version with upload features)

## Files Ready for Deployment
✅ index.html (full portfolio with upload features)
✅ portfolio.html (simplified version)
✅ .nojekyll (for GitHub Pages)
✅ All styling and functionality included
