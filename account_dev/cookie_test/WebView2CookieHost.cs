using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows.Forms;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

static class Program
{
    [STAThread]
    static void Main(string[] args) // args: [cookie_test folder], ["login" or "refresh"]
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Application.Run(new CookieForm(args[0], args[1]));
    }
}

public class CookieForm : Form
{
    const string YoutubeUrl = "https://www.youtube.com/";
    const string YouPageUrl = "https://www.youtube.com/feed/you";
    const string SuccessPageUrl = "file:///c:/Users/yy950/Desktop/JaTubePlayer%202.0/_internal/google_login_suc_red_page.html";
    const string LogoutUrl = "https://accounts.google.com/Logout";
    const string SignInUrl = "https://accounts.google.com/v3/signin/identifier" +
                             "?continue=https%3A%2F%2Fwww.youtube.com%2F" +
                             "&service=youtube&flowName=GlifWebSignIn&flowEntry=ServiceLogin";

    readonly string profileDir;
    readonly string scriptPath;
    readonly string encryptedCookieKeyPath = ""; // pending: Python will decide this path later.
    readonly string mode;
    readonly WebView2 view = new WebView2 { Dock = DockStyle.Fill };
    bool checking;
    bool done;
    bool signInStarted;
    bool showingSuccess;

    public CookieForm(string rootDir, string mode)
    {
        profileDir = Path.Combine(rootDir, "account", "profile");
        scriptPath = Path.Combine(rootDir, "user_data", "account_info.js");
        this.mode = mode;

        Text = "YouTube WebView2 Cookie Login";
        Width = 1100;
        Height = 760;
        Controls.Add(view);
        Shown += async (sender, args) => await Start();
    }

    async Task Start()
    {
        Directory.CreateDirectory(profileDir);

        // Use our own WebView2 profile. Never touch the user's real browser profile.
        var env = await CoreWebView2Environment.CreateAsync(
            null,
            profileDir,
            new CoreWebView2EnvironmentOptions("--disable-extensions")
        );
        await view.EnsureCoreWebView2Async(env);

        // Keep the WebView small and locked down.
        view.CoreWebView2.Settings.AreDevToolsEnabled = false;
        view.CoreWebView2.Settings.AreDefaultContextMenusEnabled = false;
        view.CoreWebView2.Settings.AreHostObjectsAllowed = false;
        view.CoreWebView2.Settings.AreBrowserAcceleratorKeysEnabled = false;
        view.CoreWebView2.Settings.IsWebMessageEnabled = false;

        view.CoreWebView2.NavigationStarting += (sender, args) =>
        {
            // Log only safe URLs. Query strings can contain login tokens.
            Log("navigation starting: " + SafeUrl(args.Uri));
            if (Allowed(args.Uri)) return;
            args.Cancel = true;
            Log("blocked redirect: " + SafeUrl(args.Uri));
        };

        view.CoreWebView2.NewWindowRequested += (sender, args) =>
        {
            args.Handled = true;
            Log("new-window redirect: " + SafeUrl(args.Uri));
            if (Allowed(args.Uri)) view.CoreWebView2.Navigate(args.Uri);
            else Log("blocked new-window redirect: " + SafeUrl(args.Uri));
        };

        view.CoreWebView2.NavigationCompleted += async (sender, args) =>
        {
            string url = view.CoreWebView2.Source;
            Log("navigation completed: " + SafeUrl(url));

            if (showingSuccess && SuccessPage(url))
            {
                ShowLoadedSuccessPage();
                return;
            }

            // Logout first, then open the YouTube sign-in page.
            if (mode == "login" && !signInStarted && AccountHost(url))
            {
                signInStarted = true;
                Log("navigating to account sign-in");
                view.CoreWebView2.Navigate(SignInUrl);
                return;
            }

            if (YoutubeHost(url))
            {
                if (Visible)
                {
                    Log("hiding window");
                    Hide();
                }

                await CheckCookies();
            }
        };

        view.CoreWebView2.Navigate(mode == "refresh" ? YoutubeUrl : LogoutUrl);
    }

    async Task CheckCookies()
    {
        if (checking || done) return;
        checking = true;

        try
        {
            // Wait until WebView2 has a YouTube login cookie.
            while (!await HasLoginCookie())
            {
                Log("youtube reached, cookie not valid yet");
                await Task.Delay(1000);
            }

            if (!SafeUrl(view.CoreWebView2.Source).Equals(YouPageUrl, StringComparison.OrdinalIgnoreCase))
            {
                Log("navigating to You page");
                view.CoreWebView2.Navigate(YouPageUrl);
                return;
            }
            //MessageBox.Show("YouTube login cookie found. Reading account info.", "Cookie Found");

            // Print only account info. Do not print raw cookies.
            string json = await ReadAccountInfo();
            done = true;
            Log("account info json: " + json);
            Console.Out.WriteLine(json);
            Console.Out.Flush();
            ShowSuccessPage();
        }
        finally
        {
            checking = false;
        }
    }

    async Task<bool> HasLoginCookie()
    {
        var cookies = await view.CoreWebView2.CookieManager.GetCookiesAsync(YoutubeUrl);
        bool sid = false, apisid = false, loginInfo = false;

        foreach (CoreWebView2Cookie c in cookies)
        {
            if (c.Name == "SID") sid = true;
            if (c.Name == "APISID") apisid = true;
            if (c.Name == "LOGIN_INFO") loginInfo = true;
        }

        cookies.Clear();
        // Same simple validation as the Android flow: LOGIN_INFO or SID + APISID.
        return loginInfo || (sid && apisid);
    }

    void EncryptCookies(IReadOnlyList<CoreWebView2Cookie> cookies)
    {
        //TODO
    }


    async Task<string> ReadAccountInfo()
    {
        string script = File.ReadAllText(scriptPath, Encoding.UTF8);
        string json = "{}";

        for (int i = 0; i < 40; i++)
        {
            json = await view.CoreWebView2.ExecuteScriptAsync(script);
            if (String.IsNullOrWhiteSpace(json) || json == "null") json = "{}";
            if (HasInfo(json)) return json;

            if (i == 0 || i == 39) Log("account info debug: " + json);
            await Task.Delay(250);
        }

        return json;
    }

    static bool HasInfo(string json) =>
        json.Contains("\"user_name\":\"") && !json.Contains("\"user_name\":\"\"") ||
        json.Contains("\"user_mail\":\"") && !json.Contains("\"user_mail\":\"\"");

    void ShowSuccessPage()
    {
        showingSuccess = true;
        Log("loading success page");
        view.CoreWebView2.Navigate(SuccessPageUrl);
    }

    void ShowLoadedSuccessPage()
    {
        Log("showing success page");
        Show();
        WindowState = FormWindowState.Normal;
        Activate();
    }

    static bool Allowed(string url) => YoutubeHost(url) || AccountHost(url) || SuccessPage(url);

    static bool SuccessPage(string url) =>
        SafeUrl(url).Equals(SuccessPageUrl, StringComparison.OrdinalIgnoreCase);

    static bool YoutubeHost(string url)
    {
        string host = Host(url);
        return host == "youtube.com" || host == "www.youtube.com" || host.EndsWith(".youtube.com");
    }

    static bool AccountHost(string url)
    {
        string host = Host(url);
        return host == "accounts.google.com" || host == "accounts.youtube.com" || host.StartsWith("accounts.google.");
    }

    static string Host(string url) =>
        Uri.TryCreate(url, UriKind.Absolute, out Uri uri) ? uri.Host.ToLowerInvariant() : "";

    static string SafeUrl(string url) =>
        Uri.TryCreate(url, UriKind.Absolute, out Uri uri) ? uri.GetLeftPart(UriPartial.Path) : "";

    static void Log(string message)
    {
        Console.Error.WriteLine("[wv2] " + message);
        Console.Error.Flush();
    }
}
