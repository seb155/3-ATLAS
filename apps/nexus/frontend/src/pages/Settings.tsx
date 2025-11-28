import { Settings as SettingsIcon, User, Palette, Bell, Shield, Database } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { useAppStore } from '@/stores/useAppStore';
import { useThemeStore } from '@/stores/useThemeStore';

export function Settings() {
  const { sidebarOpen, toggleSidebar } = useAppStore();
  const { activeThemeId, setTheme, getAllThemes } = useThemeStore();

  // Get current theme to determine if it's light or dark
  const currentTheme = getAllThemes().find(t => t.id === activeThemeId);
  const theme = currentTheme?.type || 'dark';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground mt-2">
          Configure your Nexus experience
        </p>
      </div>

      {/* Appearance */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Palette className="h-5 w-5 text-primary" />
            <CardTitle>Appearance</CardTitle>
          </div>
          <CardDescription>Customize how Nexus looks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-sm">Theme</p>
                <p className="text-xs text-muted-foreground">Choose your preferred color scheme</p>
              </div>
              <div className="flex gap-2">
                <Button
                  variant={theme === 'dark' ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => {
                    // Switch to a dark theme (default: catppuccin-mocha)
                    const darkTheme = getAllThemes().find(t => t.type === 'dark');
                    if (darkTheme) setTheme(darkTheme.id);
                  }}
                >
                  Dark
                </Button>
                <Button
                  variant={theme === 'light' ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => {
                    // Switch to a light theme (default: catppuccin-latte)
                    const lightTheme = getAllThemes().find(t => t.type === 'light');
                    if (lightTheme) setTheme(lightTheme.id);
                  }}
                >
                  Light
                </Button>
              </div>
            </div>

            <div className="border-t border-border pt-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-sm">Sidebar</p>
                  <p className="text-xs text-muted-foreground">Show or hide the navigation sidebar</p>
                </div>
                <Button variant="outline" size="sm" onClick={toggleSidebar}>
                  {sidebarOpen ? 'Hide' : 'Show'}
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Profile (Coming Soon) */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <User className="h-5 w-5 text-primary" />
            <CardTitle>Profile</CardTitle>
          </div>
          <CardDescription>Manage your account settings</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="py-6 text-center">
            <Badge variant="info">Coming in Phase 2</Badge>
            <p className="text-sm text-muted-foreground mt-2">
              User authentication and profile management will be available when we add the backend
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Notifications (Coming Soon) */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5 text-primary" />
            <CardTitle>Notifications</CardTitle>
          </div>
          <CardDescription>Configure notification preferences</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="py-6 text-center">
            <Badge variant="info">Coming in Phase 6</Badge>
            <p className="text-sm text-muted-foreground mt-2">
              Notification settings will be available with collaboration features
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Security (Coming Soon) */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" />
            <CardTitle>Security</CardTitle>
          </div>
          <CardDescription>Manage security settings</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="py-6 text-center">
            <Badge variant="info">Coming in Phase 2</Badge>
            <p className="text-sm text-muted-foreground mt-2">
              Password, 2FA, and security settings will be available with authentication
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Data & Storage (Coming Soon) */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Database className="h-5 w-5 text-primary" />
            <CardTitle>Data & Storage</CardTitle>
          </div>
          <CardDescription>Manage your data and backups</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="py-6 text-center">
            <Badge variant="info">Coming in Phase 2+</Badge>
            <p className="text-sm text-muted-foreground mt-2">
              Data export, import, and backup features will be available with the database
            </p>
          </div>
        </CardContent>
      </Card>

      {/* System Info */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <SettingsIcon className="h-5 w-5 text-primary" />
            <CardTitle>System Information</CardTitle>
          </div>
          <CardDescription>Current system status</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-muted-foreground">Version</p>
              <p className="font-medium">v0.1.0-alpha</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Phase</p>
              <p className="font-medium">Phase 1 Complete</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Status</p>
              <Badge variant="success">Running</Badge>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Mode</p>
              <p className="font-medium">Development</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
