Add-Type -Language CSharp -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Text;

public enum EDataFlow { eRender=0, eCapture=1, eAll=2 }
public enum ERole { eConsole=0, eMultimedia=1, eCommunications=2 }
[Flags] public enum DeviceState { Active=1, Disabled=2, NotPresent=4, Unplugged=8, All=15 }

[ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
public class MMDeviceEnumeratorComObject { }

[ComImport, Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDeviceEnumerator {
    int EnumAudioEndpoints(EDataFlow dataFlow, DeviceState dwStateMask, out IMMDeviceCollection ppDevices);
    int GetDefaultAudioEndpoint(EDataFlow dataFlow, ERole role, out IMMDevice ppEndpoint);
    int GetDevice([MarshalAs(UnmanagedType.LPWStr)] string pwstrId, out IMMDevice ppDevice);
    int RegisterEndpointNotificationCallback(IntPtr pClient);
    int UnregisterEndpointNotificationCallback(IntPtr pClient);
}

[ComImport, Guid("0BD7A1BE-7A1A-44DB-8397-C0AFB0911F34"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDeviceCollection {
    int GetCount(out uint pcDevices);
    int Item(uint nDevice, out IMMDevice ppDevice);
}

[ComImport, Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDevice {
    int Activate(ref Guid iid, int dwClsCtx, IntPtr pActivationParams, [MarshalAs(UnmanagedType.IUnknown)] out object ppInterface);
    int OpenPropertyStore(int stgmAccess, out IPropertyStore ppProperties);
    int GetId([MarshalAs(UnmanagedType.LPWStr)] out string ppstrId);
    int GetState(out DeviceState pdwState);
}

[ComImport, Guid("886d8eeb-8cf2-4446-8d02-cdba1dbdcf99"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IPropertyStore {
    int GetCount(out uint cProps);
    int GetAt(uint iProp, out PROPERTYKEY pkey);
    int GetValue(ref PROPERTYKEY key, out PROPVARIANT pv);
    int SetValue(ref PROPERTYKEY key, ref PROPVARIANT propvar);
    int Commit();
}

[StructLayout(LayoutKind.Sequential)]
public struct PROPERTYKEY { public Guid fmtid; public uint pid; }

[StructLayout(LayoutKind.Sequential)]
public struct PROPVARIANT {
    public ushort vt; public ushort wReserved1; public ushort wReserved2; public ushort wReserved3;
    public IntPtr p;
    public int p2;
}

[ComImport, Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IAudioEndpointVolume {
    int RegisterControlChangeNotify(IntPtr pNotify);
    int UnregisterControlChangeNotify(IntPtr pNotify);
    int GetChannelCount(out uint pnChannelCount);
    int SetMasterVolumeLevel(float fLevelDB, Guid pguidEventContext);
    int SetMasterVolumeLevelScalar(float fLevel, Guid pguidEventContext);
    int GetMasterVolumeLevel(out float pfLevelDB);
    int GetMasterVolumeLevelScalar(out float pfLevel);
    int SetChannelVolumeLevel(uint nChannel, float fLevelDB, Guid pguidEventContext);
    int SetChannelVolumeLevelScalar(uint nChannel, float fLevel, Guid pguidEventContext);
    int GetChannelVolumeLevel(uint nChannel, out float pfLevelDB);
    int GetChannelVolumeLevelScalar(uint nChannel, out float pfLevel);
    int SetMute(bool bMute, Guid pguidEventContext);
    int GetMute(out bool pbMute);
    int GetVolumeStepInfo(out uint pnStep, out uint pnStepCount);
    int VolumeStepUp(Guid pguidEventContext);
    int VolumeStepDown(Guid pguidEventContext);
    int QueryHardwareSupport(out uint pdwHardwareSupportMask);
    int GetVolumeRange(out float pflVolumeMindB, out float pflVolumeMaxdB, out float pflVolumeIncrementdB);
}

[ComImport, Guid("f8679f50-850a-41cf-9c72-430f290290c8"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IPolicyConfig {
    int GetMixFormat([MarshalAs(UnmanagedType.LPWStr)] string pszDeviceName, IntPtr ppFormat);
    int GetDeviceFormat([MarshalAs(UnmanagedType.LPWStr)] string pszDeviceName, int bDefault, IntPtr ppFormat);
    int ResetDeviceFormat([MarshalAs(UnmanagedType.LPWStr)] string pszDeviceName);
    int SetDeviceFormat([MarshalAs(UnmanagedType.LPWStr)] string pszDeviceName, IntPtr pEndpointFormat, IntPtr mixFormat);
    int GetProcessingPeriod([MarshalAs(UnmanagedType.LPWStr)] string pszDeviceName, int bDefault, IntPtr pmftDefault, IntPtr pmftMinimum);
    int SetProcessingPeriod([MarshalAs(UnmanagedType.LPWStr)] string pszDeviceName, IntPtr pmftPeriod);
    int GetShareMode([MarshalAs(UnmanagedType.LPWStr)] string pszDeviceName, IntPtr pMode);
    int SetShareMode([MarshalAs(UnmanagedType.LPWStr)] string pszDeviceName, IntPtr mode);
    int GetPropertyValue([MarshalAs(UnmanagedType.LPWStr)] string pszDeviceName, ref PROPERTYKEY key, IntPtr pv);
    int SetPropertyValue([MarshalAs(UnmanagedType.LPWStr)] string pszDeviceName, ref PROPERTYKEY key, ref PROPVARIANT pv);
    int SetDefaultEndpoint([MarshalAs(UnmanagedType.LPWStr)] string pszDeviceName, ERole role);
    int SetEndpointVisibility([MarshalAs(UnmanagedType.LPWStr)] string pszDeviceName, int bVisible);
}

[ComImport, Guid("870af99c-171d-4f9e-af0d-e63df40c2bc9")]
public class PolicyConfigClient { }

public class AudioUtil {
    static PROPERTYKEY PKEY_Device_FriendlyName = new PROPERTYKEY(){ fmtid = new Guid("a45c254e-df1c-4efd-8020-67d146a850e0"), pid = 14 };
    public static string GetName(IMMDevice dev) {
        IPropertyStore store; dev.OpenPropertyStore(0, out store);
        PROPVARIANT pv; store.GetValue(ref PKEY_Device_FriendlyName, out pv);
        string s = Marshal.PtrToStringUni(pv.p);
        return s;
    }
    public static IAudioEndpointVolume GetVolume(IMMDevice dev) {
        Guid iid = new Guid("5CDF2C82-841E-4546-9722-0CF74078229A"); object obj;
        dev.Activate(ref iid, 23, IntPtr.Zero, out obj);
        return (IAudioEndpointVolume)obj;
    }
    public static IMMDeviceEnumerator Enumerator() {
        object o = new MMDeviceEnumeratorComObject();
        IntPtr p = Marshal.GetIUnknownForObject(o);
        try { return (IMMDeviceEnumerator)Marshal.GetTypedObjectForIUnknown(p, typeof(IMMDeviceEnumerator)); }
        finally { Marshal.Release(p); }
    }
    public static IPolicyConfig Policy() {
        object o = new PolicyConfigClient();
        IntPtr p = Marshal.GetIUnknownForObject(o);
        try { return (IPolicyConfig)Marshal.GetTypedObjectForIUnknown(p, typeof(IPolicyConfig)); }
        finally { Marshal.Release(p); }
    }
    public static void SetDefault(string id) { var pc=Policy(); pc.SetDefaultEndpoint(id, ERole.eConsole); pc.SetDefaultEndpoint(id, ERole.eMultimedia); pc.SetDefaultEndpoint(id, ERole.eCommunications); }
}
'@

$enum=[AudioUtil]::Enumerator()
$defaultIds=@{}
foreach($role in @([ERole]::eConsole,[ERole]::eMultimedia,[ERole]::eCommunications)){
  $d=$null; $hr=$enum.GetDefaultAudioEndpoint([EDataFlow]::eCapture,$role,[ref]$d)
  if($hr -eq 0 -and $d){ $id=''; $d.GetId([ref]$id) | Out-Null; $defaultIds[$role.ToString()]=$id }
}
$col=$null; $enum.EnumAudioEndpoints([EDataFlow]::eCapture,[DeviceState]::All,[ref]$col) | Out-Null
$count=0; $col.GetCount([ref]$count) | Out-Null
$devices=@()
for($i=0; $i -lt $count; $i++){
  $dev=$null; $col.Item([uint32]$i,[ref]$dev) | Out-Null
  $id=''; $state=[DeviceState]::All; $dev.GetId([ref]$id) | Out-Null; $dev.GetState([ref]$state) | Out-Null
  $name=[AudioUtil]::GetName($dev)
  $vol=$null; $scalar=$null; $mute=$null
  if($state -eq [DeviceState]::Active){ try { $vol=[AudioUtil]::GetVolume($dev); [single]$s=0; [bool]$m=$false; $vol.GetMasterVolumeLevelScalar([ref]$s)|Out-Null; $vol.GetMute([ref]$m)|Out-Null; $scalar=[Math]::Round($s*100,1); $mute=$m } catch {} }
  $roles=($defaultIds.GetEnumerator() | Where-Object {$_.Value -eq $id} | ForEach-Object {$_.Key}) -join ','
  $devices += [PSCustomObject]@{Index=$i; Name=$name; State=$state.ToString(); VolumePct=$scalar; Muted=$mute; DefaultRoles=$roles; Id=$id}
}
if($args[0] -eq 'fix-aula'){
  $target=$devices | Where-Object { $_.Name -like '*AULA-G7Pro*' -and $_.State -eq 'Active' } | Select-Object -First 1
  if(-not $target){ throw 'Active AULA-G7Pro capture endpoint not found' }
  $dev=$null; $enum.GetDevice($target.Id,[ref]$dev)|Out-Null
  $vol=[AudioUtil]::GetVolume($dev)
  $g=[Guid]::Empty
  $vol.SetMute($false,$g)|Out-Null
  $vol.SetMasterVolumeLevelScalar(1.0,$g)|Out-Null
  [AudioUtil]::SetDefault($target.Id)
  Write-Output "Changed: unmuted + volume 100% + set default capture endpoint to $($target.Name)"
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $MyInvocation.MyCommand.Path
} else {
  $devices | Sort-Object State,Name | Format-Table -AutoSize
}
