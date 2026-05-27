using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

internal static class GuiLauncher
{
    [STAThread]
    private static int Main()
    {
        string repoRoot = AppDomain.CurrentDomain.BaseDirectory;
        string[] candidates =
        {
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Windows), "pyw.exe"),
            "pyw.exe",
            "pythonw.exe",
            "py.exe",
            "python.exe"
        };

        foreach (string candidate in candidates)
        {
            if (TryStart(candidate, repoRoot))
            {
                return 0;
            }
        }

        MessageBox.Show(
            "Python konnte nicht gestartet werden. Bitte pruefe, ob Python installiert ist.",
            "W-MIDI",
            MessageBoxButtons.OK,
            MessageBoxIcon.Error
        );
        return 1;
    }

    private static bool TryStart(string executable, string repoRoot)
    {
        try
        {
            string arguments = executable.EndsWith("py.exe", StringComparison.OrdinalIgnoreCase)
                || executable.EndsWith("pyw.exe", StringComparison.OrdinalIgnoreCase)
                    ? "-3 -m midi_wled_bridge.gui"
                    : "-m midi_wled_bridge.gui";

            ProcessStartInfo startInfo = new ProcessStartInfo
            {
                FileName = executable,
                Arguments = arguments,
                WorkingDirectory = repoRoot,
                UseShellExecute = false,
                CreateNoWindow = true,
            };
            Process.Start(startInfo);
            return true;
        }
        catch
        {
            return false;
        }
    }
}
