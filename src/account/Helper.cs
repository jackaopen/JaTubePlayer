using System;
using System.Collections.Generic;
using System.Text;
using System.Text.Json;
using Microsoft.Web.WebView2.Core;
using System.Reflection;
using System.IO;
using System.Linq;


static class Helper
{
        public static HashSet<string> LoadGoogleAccountHosts()
        {
            using Stream? stream =
                Assembly.GetExecutingAssembly()
                    .GetManifestResourceStream("chrome_supported_domain.txt");

            if (stream == null)
                {
                    ErrorLog("missing chrome_supported_domain");
                    Environment.Exit(1);
                }

            using var reader = new StreamReader(stream);
            return reader.ReadToEnd()
                .Split(
                    (char[]?)null,
                    StringSplitOptions.RemoveEmptyEntries |
                    StringSplitOptions.TrimEntries
                )
                .Select(suffix => "accounts" + suffix)// .google.[localcode] -> accounts.google.[localcode]
                .Append("accounts.youtube.com")
                .ToHashSet(StringComparer.OrdinalIgnoreCase);
        }    
    
    
    
    public static string BuildCookieHeader(IReadOnlyList<CoreWebView2Cookie> cookies)
    {
        StringBuilder builder = new StringBuilder();

        foreach (CoreWebView2Cookie cookie in cookies)
        {
            if (builder.Length > 0)
            {
                builder.Append("; ");
            }

            builder.Append(cookie.Name);
            builder.Append('=');
            builder.Append(cookie.Value);
        }

        return builder.ToString();
    }

    public static bool HasInfo(string json)
    {
        try
        {
            string[]? values = JsonSerializer.Deserialize<string[]>(json);
            return values?.Length == 2 &&
                !String.IsNullOrWhiteSpace(values[0]) &&
                !String.IsNullOrWhiteSpace(values[1]);
        }
        catch (JsonException)
        {
            return false;
        }
    }



    public static bool Allowed(string url) => YoutubeHost(url) || AccountHost(url) || SuccessPage(url);


    public static bool YoutubeHost(string url)
    {
        string host = Host(url);
        if(!TryGetHttpsUri(url))return false;
        return host == "youtube.com" || host == "www.youtube.com" ;
    }

    public static bool AccountHost(string url)
    {
        string host = Host(url);
        if(!TryGetHttpsUri(url))return false;
        return host == "accounts.google.com" || host == "accounts.youtube.com"
            || host == "gds.google.com" || host == "myaccount.google.com" || host == "consent.youtube.com";
    }

    public static bool SuccessPage(string url)
    {
        if (!Uri.TryCreate(url, UriKind.Absolute, out Uri? uri) || !uri.IsFile)
            return false;

        string localPath = Path.GetFullPath(uri.LocalPath);
        string packedRoot = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "_internal"));
        string devRoot = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "_internal"));
        string[] allowedFiles =
        {
            "google_login_suc_red_page.html",
            "google_login_waiting_page.html",
            "google_login_err_screen.html"
        };

        return allowedFiles.Any(fileName =>
            string.Equals(localPath, Path.Combine(packedRoot, fileName), StringComparison.OrdinalIgnoreCase) ||
            string.Equals(localPath, Path.Combine(devRoot, fileName), StringComparison.OrdinalIgnoreCase));
    }


    static string Host(string url) =>
        Uri.TryCreate(url, UriKind.Absolute, out Uri? uri) ? uri.Host.ToLowerInvariant() : "";

    public static string LeftPartialToPath(string url) =>
        Uri.TryCreate(url, UriKind.Absolute, out Uri? uri) ? uri.GetLeftPart(UriPartial.Path) : "";
    static bool TryGetHttpsUri(string url)
    {
        Uri? uri;
        return Uri.TryCreate(url, UriKind.Absolute, out uri) &&
            uri.Scheme.Equals(
                Uri.UriSchemeHttps,
                StringComparison.OrdinalIgnoreCase
            ) &&
            uri.Port == 443;
    }

    public static void Log(string message)
    {
        Console.Out.WriteLine("[wv2] " + message);
        Console.Out.Flush();
    }
    
    public static void ErrorLog(string message)
    {
        Console.Error.Write("[wv2]" + message);
        Console.Error.Flush();
    }
}


