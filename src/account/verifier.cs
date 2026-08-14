using System.IO;
using System.Security.Cryptography;
using System;

static class Verifier
{
    static string ErrPageHash = "82fd2e536bad20b7a71326dfaa9e97290fcd59c4f714161cd8f7c7307c8af2f2";
    static string SucPageHash = "741b4977a6e6b0e850a7e704981e4f9bc8f04e43f6504edb4e864a7cfed4a558";
    static string WaitPageHash ="d44fddb564bb8017671d4c8141548e5fd6a9d7b2e6b4d335bab992b223af2e23";
    public static bool verifyToken(string appdataDir,byte[]InputToken){
        byte[]? ExpectedToken = null;
        try
        {
            string tokenpath = Path.Combine(appdataDir,"JaTubePlayer","account_token.enc");
            byte[] encryptedKey = File.ReadAllBytes(tokenpath);
            
            ExpectedToken=  ProtectedData.Unprotect(
                    encryptedKey,
                    optionalEntropy: null,
                    scope: DataProtectionScope.CurrentUser
                    );

            return CryptographicOperations.FixedTimeEquals(
                InputToken,
                ExpectedToken
            );
                }
        catch(Exception e)
        {
            Helper.ErrorLog(e.ToString());
            return false;
        }
        finally
        {
            if(ExpectedToken is not null){
                CryptographicOperations.ZeroMemory(ExpectedToken);}
        }
        
    }
    public static bool verifyDir(string inputDir)

    {
        string expectedDir = Path.TrimEndingDirectorySeparator(
            Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,"..",".."))
        );

        string expectedDir_packed = Path.TrimEndingDirectorySeparator(
            Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,".."))
        );
        string TrimedInputDir = Path.TrimEndingDirectorySeparator(
            Path.GetFullPath(inputDir)
        );
        Helper.ErrorLog($"Expected directory: {expectedDir}");
        Helper.ErrorLog($"Input directory: {TrimedInputDir}");

        return string.Equals(expectedDir,
                    TrimedInputDir,
                    StringComparison.OrdinalIgnoreCase)||
                    string.Equals(expectedDir_packed,
                    TrimedInputDir,
                    StringComparison.OrdinalIgnoreCase);
    }
    private static string calculatFileHash(string targetfile)
    {   
        var sha256 = SHA256.Create();
        using(var fileStream = new FileStream(targetfile, FileMode.Open, FileAccess.Read, FileShare.None))
        {
            var hashBytes = sha256.ComputeHash(fileStream);
            return BitConverter.ToString(hashBytes).Replace("-", "").ToLowerInvariant();
        }
    }
    public static bool verifyLocalResources(string rootDir)
    {
        string SuccessPagePath = Path.Combine(rootDir, "_internal", "google_login_suc_red_page.html");
        string WaitingPagePath = Path.Combine(rootDir,"_internal", "google_login_waiting_page.html");
        string ErrorPagePath = Path.Combine(rootDir,"_internal", "google_login_err_screen.html");
        return  calculatFileHash(ErrorPagePath)==ErrPageHash&&
                calculatFileHash(SuccessPagePath)==SucPageHash&&
                calculatFileHash(WaitingPagePath)==WaitPageHash;
    }
}