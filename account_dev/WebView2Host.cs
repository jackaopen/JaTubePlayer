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



public class Helper
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
        return host == "youtube.com" || host == "www.youtube.com" || host.EndsWith(".youtube.com");
    }

    public static bool AccountHost(string url)
    {
        string host = Host(url);
        return host == "accounts.google.com" || host == "accounts.youtube.com" || host.StartsWith("accounts.google.");
    }

    public static bool SuccessPage(string url) =>
        Uri.TryCreate(url, UriKind.Absolute, out Uri uri) &&
        uri.IsFile &&
        (uri.LocalPath.EndsWith("google_login_suc_red_page.html", StringComparison.OrdinalIgnoreCase)||
        uri.LocalPath.EndsWith("google_login_waiting_page.html", StringComparison.OrdinalIgnoreCase));

    static string Host(string url) =>
        Uri.TryCreate(url, UriKind.Absolute, out Uri uri) ? uri.Host.ToLowerInvariant() : "";

    public static string SafeUrl(string url) =>
        Uri.TryCreate(url, UriKind.Absolute, out Uri uri) ? uri.GetLeftPart(UriPartial.Path) : "";

    public static void Log(string message)
    {
        Console.Error.WriteLine("[wv2] " + message);
        Console.Error.Flush();
    }
}




public class CookieForm : Form
{
    const string YoutubeUrl = "https://www.youtube.com/";
    const string YouPageUrl = "https://www.youtube.com/feed/you";
    
    const string LogoutUrl = "https://accounts.google.com/Logout";
    const string SignInUrl = "https://accounts.google.com/v3/signin/identifier" +
                             "?continue=https%3A%2F%2Fwww.youtube.com%2F" +
                             "&service=youtube&flowName=GlifWebSignIn&flowEntry=ServiceLogin";

    readonly string profileDir;
    string SuccessPagePath = "";
    string WaitingPagePath = "";
    readonly string scriptPath;
    readonly string EncryptedCookieKeyPath = ""; // pending: Python will decide this path later.
    readonly string mode;
    readonly string keyPath = "";
    readonly WebView2 view = new WebView2 { Dock = DockStyle.Fill };
    bool checking;
    bool done;
    bool signInStarted;
    bool showingSuccess;
    bool waitingShown;
    CookieForm waitingForm;
    private Task startTask;
    private Task EnsureStartedAsync()
        {
            return startTask ??= Start();
        }


    public CookieForm(string rootDir, string mode)
    {
        
        

        profileDir = Path.Combine(rootDir, "account", "profile");
        scriptPath = Path.Combine(rootDir, "_internal", "account_info.js");
        keyPath = Path.Combine(rootDir, "user_data", "AES_key.enc");

        EncryptedCookieKeyPath = Path.Combine(rootDir, "user_data", "cookie_key.enc");
        SuccessPagePath = Path.Combine(rootDir, "_internal", "google_login_suc_red_page.html");
        WaitingPagePath = Path.Combine(rootDir,"_internal", "google_login_waiting_page.html");
        
        this.mode = mode;

        Text = mode == "process" ? "Processing" : "YouTube WebView2 Cookie Login";
        Width = mode == "process" ? 560 : 1100;
        Height = mode == "process" ? 360 : 760;
        Controls.Add(view);
        if (mode == "refresh")
        {
            Opacity = 0.0;
        }
        if(mode=="login"){Shown += async (sender, args) => await EnsureStartedAsync();}
        else if (mode=="refresh"){Shown += async (sender, args) => await refresh();}

        
        if (mode != "process") {
            waitingForm = new CookieForm(rootDir, "process");
            waitingForm.FormClosed += (sender, args) =>
            {
                {
                    Helper.Log("waiting form closed, exiting");
                    Close();
                }
            };
        }
    }

    


    async Task Start()
    {
        // Start the primary WebView with a fresh profile. The processing/waiting
        // form shares this directory, so it must not delete the active profile.

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
        if (mode == "process")
        {
            view.CoreWebView2.WindowCloseRequested += (sender, args) => Close();
        }
        
        view.CoreWebView2.NavigationStarting += async (sender, args) =>
        {
            if (mode == "process")
            {
                if (Helper.Allowed(args.Uri))
                {
                    return;
                }
                args.Cancel = true;
                return;
            }
            // mode = login or refresh

            // Log only safe URLs. Query strings can contain login tokens.
            Helper.Log("navigation starting: " + Helper.SafeUrl(args.Uri));
            if (Helper.YoutubeHost(args.Uri) && waitingForm != null && !waitingShown)
            {
                waitingShown = true;
                waitingForm.StartPosition = FormStartPosition.Manual;
                waitingForm.Bounds = Bounds;
                waitingForm.WindowState = WindowState == FormWindowState.Minimized
                    ? FormWindowState.Normal
                    : WindowState;
                waitingForm.Show();
                await waitingForm.NavigateAsync(WaitingPagePath);
                waitingForm.Activate();
                Hide();
            }

            if (Helper.Allowed(args.Uri)) return;

            args.Cancel = true;
            Helper.Log("blocked redirect: " + Helper.SafeUrl(args.Uri));
        };

        view.CoreWebView2.NewWindowRequested += (sender, args) =>
        {
            args.Handled = true;
            Helper.Log("new-window redirect: " + Helper.SafeUrl(args.Uri));
            if (Helper.Allowed(args.Uri)) view.CoreWebView2.Navigate(args.Uri);
            else Helper.Log("blocked new-window redirect: " + Helper.SafeUrl(args.Uri));
        };

        view.CoreWebView2.NavigationCompleted += async (sender, args) =>
        {
            string url = view.CoreWebView2.Source;
            Helper.Log("navigation completed: " + Helper.SafeUrl(url));
            bool successPageLoaded = Helper.SafeUrl(url).Equals(SuccessPagePath, StringComparison.OrdinalIgnoreCase);
            
            
            if (showingSuccess && successPageLoaded)
            {
                Helper.Log("showing success page");
                return;
            }

            // Logout first, then open the YouTube sign-in page.
            if (mode == "login" && !signInStarted && Helper.AccountHost(url))
            {
                signInStarted = true;
                Helper.Log("navigating to account sign-in");
                view.CoreWebView2.Navigate(SignInUrl);
                return;
            }

            if (Helper.YoutubeHost(url))
            {
                Helper.Log("hiding window");
                
                await CheckCookies();
            }
        };
        view.CoreWebView2.WindowCloseRequested += (sender, args) =>
        {
            Helper.Log("window close requested");
            Close();
        };
        view.CoreWebView2.Navigate(mode == "refresh" ? YoutubeUrl : LogoutUrl);
    }



    public async Task NavigateAsync(string path)
    {
        await EnsureStartedAsync();
        view.CoreWebView2.Navigate(new Uri(path).AbsoluteUri);
    }

    async Task refresh()

    {
        Directory.CreateDirectory(profileDir);
        Hide();
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
            Hide();
            if (Helper.Allowed(args.Uri)) return;

            args.Cancel = true;
            Helper.Log("blocked redirect: " + Helper.SafeUrl(args.Uri));
        };

        view.CoreWebView2.NewWindowRequested += (sender, args) =>
        {
            args.Handled = true;
            Helper.Log("new-window redirect: " + Helper.SafeUrl(args.Uri));
            if (Helper.Allowed(args.Uri)) view.CoreWebView2.Navigate(args.Uri);
            else Helper.Log("blocked new-window redirect: " + Helper.SafeUrl(args.Uri));
        };

        view.CoreWebView2.NavigationCompleted += async (sender, args) =>
        {
            string url = view.CoreWebView2.Source;
            Helper.Log("navigation completed: " + Helper.SafeUrl(url));

            if (Helper.YoutubeHost(url))
            {
                await CheckCookies();
                if (done)Close();
            }
        };

        view.CoreWebView2.Navigate(YoutubeUrl);
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
                Helper.Log("youtube reached, cookie not valid yet");
                await Task.Delay(1000);
            }

            if (!Helper.SafeUrl(view.CoreWebView2.Source).Equals(YouPageUrl, StringComparison.OrdinalIgnoreCase))
            {
                Helper.Log("navigating to You page");
                view.CoreWebView2.Navigate(YouPageUrl);
                return;
            }
            //MessageBox.Show("YouTube login cookie found. Reading account info.", "Cookie Found");

            // Print only account info. Do not print raw cookies.
            string json = await ReadAccountInfo();
            var cookies = await view.CoreWebView2.CookieManager.GetCookiesAsync(YoutubeUrl);
            EncryptCookies(cookies);
            cookies.Clear();
            done = true;
            Helper.Log("account info json: " + json);
            Console.Out.WriteLine(json);
            Console.Out.Flush();
            showingSuccess = true;
            Helper.Log("loading success page");
            await waitingForm.NavigateAsync(SuccessPagePath);
            WindowState = FormWindowState.Normal;
            TopMost = true;
            Activate();
            TopMost = false;
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
        Directory.CreateDirectory(Path.GetDirectoryName(EncryptedCookieKeyPath));

        byte[] encryptedKey = File.ReadAllBytes(keyPath);
        byte[] AesKey = ProtectedData.Unprotect(
              encryptedKey,
              optionalEntropy: null,
              scope: DataProtectionScope.CurrentUser
            );
        if (AesKey.Length != 16 && AesKey.Length != 24 && AesKey.Length != 32)
        {
            throw new InvalidOperationException("Invalid AES key length.");
        }

        string cookieHeader = Helper.BuildCookieHeader(cookies);
        byte[] cookieinbyte = Encoding.UTF8.GetBytes(cookieHeader);


        byte[] nonce = RandomNumberGenerator.GetBytes(12);
        byte[] Encrypted = new byte[cookieinbyte.Length];
        byte[] tag = new byte[16];

        using AesGcm aes = new AesGcm(AesKey, 16);
        aes.Encrypt(nonce, cookieinbyte, Encrypted, tag);

        byte[] EncryptedByte = new byte[nonce.Length + tag.Length + Encrypted.Length];

        Buffer.BlockCopy(nonce, 0, EncryptedByte, 0, nonce.Length);
        Buffer.BlockCopy(tag, 0, EncryptedByte, nonce.Length, tag.Length);
        Buffer.BlockCopy(Encrypted, 0, EncryptedByte, nonce.Length + tag.Length, Encrypted.Length);

        File.WriteAllBytes(EncryptedCookieKeyPath, EncryptedByte);

        CryptographicOperations.ZeroMemory(AesKey);
        CryptographicOperations.ZeroMemory(cookieinbyte);
        CryptographicOperations.ZeroMemory(Encrypted);
        CryptographicOperations.ZeroMemory(EncryptedByte);
            
        
    }


    async Task<string> ReadAccountInfo()
    {
        string script = File.ReadAllText(scriptPath, Encoding.UTF8);
        string json = "{}";

        for (int i = 0; i < 40; i++)
        {
            json = await view.CoreWebView2.ExecuteScriptAsync(script);
            if (String.IsNullOrWhiteSpace(json) || json == "null") json = "{}";
            if (Helper.HasInfo(json)) return json;

            if (i == 0 || i == 39) Helper.Log("account info debug: " + json);
            await Task.Delay(250);
        }

        return json;
    }

    
}
