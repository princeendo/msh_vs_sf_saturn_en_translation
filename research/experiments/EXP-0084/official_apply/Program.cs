// Test A: the official SSP class (unmodified) applies each ._DFR to the files
// the official core extracted, using the local names Windows would compute.
// Prints NAME MD5-before SHA256-after for every file the patch changed.
using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Threading;
using System.Threading.Tasks;
using Helper;
using ISO9660;
using SegaSaturnPatcher;
using SSPStandard;

class ConsoleMethods : IOSMethods
{
    public bool EnablePassword { get; set; }
    public Thread MainThread => Thread.CurrentThread;
    public double WindowWidth => 0;
    public double WindowHeight => 0;
    public string OpenFileDialog(string a, string b, string c = null) => throw new InvalidOperationException(a);
    public string SaveFileDialog(string a, string b, string c = null, string d = null) => throw new InvalidOperationException(a);
    public string FolderDialog(string a, string b) => throw new InvalidOperationException(a);
    public string GetPassword() => "";
    public void DisplayAlert(string title, string message) => Console.WriteLine($"ALERT {title}: {message}");
    public Task<bool> DisplayAlert(string title, string message, string yes, string no)
    {
        Console.WriteLine($"PROMPT {title}: {message}");
        return Task.FromResult(false);
    }
    public Task OpenWindowAsync(Uri uri) => Task.CompletedTask;
}

static class Program
{
    static int Main(string[] args)
    {
        SelectedCDInfo.SelectGame("CD Image", null, args[0]);
        string output = args[2];
        Directory.CreateDirectory(output);
        SelectedCDInfo.Instance.Extract(output);
        var ip = SelectedCDInfo.Instance.IPBin;
        var ssp = new SSP(args[1], ip.Version, ip.DeviceInformation);
        Console.WriteLine($"valid={ssp.IsValid} version={ssp.VersionString} contains={ssp.ContainsContent(SelectedCDInfo.Instance.DriveFileOrder)} orders={ssp.GetFileOrders().Count}");
        var methods = new ConsoleMethods();
        foreach (var path in Directory.GetFiles(output).OrderBy(p => p, StringComparer.Ordinal))
        {
            string name = Path.GetFileName(path);
            byte[] before = System.IO.File.ReadAllBytes(path);
            ssp.ApplyPatch(name, path, methods);
            byte[] after = System.IO.File.ReadAllBytes(path);
            if (!before.SequenceEqual(after))
                Console.WriteLine($"{name} {Convert.ToHexString(MD5.HashData(before))} {Convert.ToHexString(SHA256.HashData(after)).ToLower()}");
        }
        return 0;
    }
}
