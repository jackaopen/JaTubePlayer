using System;
using System.Collections.Generic;
using System.Text;
using System.Text.Json;
using Microsoft.Web.WebView2.Core;


static class Helper
{
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
            string[] values = JsonSerializer.Deserialize<string[]>(json);
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
        return host == "youtube.com" || host == "www.youtube.com" ;
    }

    public static bool AccountHost(string url)
    {
        string host = Host(url);
        return host == "accounts.google.com" || host == "accounts.youtube.com";
    }

    public static bool SuccessPage(string url) =>
        Uri.TryCreate(url, UriKind.Absolute, out Uri uri) &&
        uri.IsFile &&
        (uri.LocalPath.EndsWith("google_login_suc_red_page.html", StringComparison.OrdinalIgnoreCase)||
        uri.LocalPath.EndsWith("google_login_waiting_page.html", StringComparison.OrdinalIgnoreCase)||
        uri.LocalPath.EndsWith("google_login_err_screen.html",StringComparison.OrdinalIgnoreCase));


    static string Host(string url) =>
        Uri.TryCreate(url, UriKind.Absolute, out Uri uri) ? uri.Host.ToLowerInvariant() : "";

    public static string LeftPartialToPath(string url) =>
        Uri.TryCreate(url, UriKind.Absolute, out Uri uri) ? uri.GetLeftPart(UriPartial.Path) : "";

    public static void Log(string message)
    {
        Console.Error.WriteLine("[wv2] " + message);
        Console.Error.Flush();
    }
}


