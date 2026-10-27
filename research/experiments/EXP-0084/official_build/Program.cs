// Runs the official Sega Saturn Patcher's unmodified core libraries the way its
// GUI does: SelectGame on a CUE, set the patch, then BuildDisc.Build.
// Usage: ssph CUE SSP|- OUTPUT.bin [multi]
using System;
using System.Threading;
using System.Threading.Tasks;
using Helper;
using ISO9660;
using SegaSaturnPatcher;

class ConsoleMethods : IOSMethods
{
    public bool EnablePassword { get; set; }
    public Thread MainThread => Thread.CurrentThread;
    public double WindowWidth => 0;
    public double WindowHeight => 0;
    public string OpenFileDialog(string a, string b, string c = null) => throw new InvalidOperationException("file dialog: " + a);
    public string SaveFileDialog(string a, string b, string c = null, string d = null) => throw new InvalidOperationException("save dialog: " + a);
    public string FolderDialog(string a, string b) => throw new InvalidOperationException("folder dialog: " + a);
    public string GetPassword() => "";
    public void DisplayAlert(string title, string message) => Console.WriteLine($"ALERT {title}: {message}");
    public Task<bool> DisplayAlert(string title, string message, string yes, string no)
    {
        Console.WriteLine($"PROMPT {title}: {message} -> {no}");
        return Task.FromResult(false);
    }
    public Task OpenWindowAsync(Uri uri) => Task.CompletedTask;
}

static class Program
{
    static int Main(string[] args)
    {
        SelectedCDInfo.SelectGame("CD Image", null, args[0]);
        if (args[1] != "-")
            SelectedCDInfo.Instance.PatchName = args[1];
        SelectedCDInfo.Instance.OutputType = OutputType.BIN;
        bool multi = args.Length > 3 && args[3] == "multi";
        bool ok = BuildDisc.Build(args[2], multi, new ConsoleMethods()).GetAwaiter().GetResult();
        Console.WriteLine($"Build returned {ok}");
        return ok ? 0 : 1;
    }
}
