import time
import hashlib

from morituri.common import common
from morituri.configure import configure
from morituri.result import result


class EacLogger(result.Logger):

    _accuratelyRipped = 0
    _inARDatabase = 0
    _errors = False

    # Overrides morituri's common implementation because EAC writes minutes
    # value without zero padding it (EAC: %2d) vs (morituri: %02d)
    def _framesToMSF(self, frames):
        """Returns MSF representation of the provided frames value"""

        f = frames % common.FRAMES_PER_SECOND
        frames -= f
        s = (frames / common.FRAMES_PER_SECOND) % 60
        frames -= s * 60
        m = frames / common.FRAMES_PER_SECOND / 60
        return "%2d:%02d.%02d" % (m, s, f)

    # Overrides morituri's common implementation because EAC writes hours
    # value without zero padding it (EAC: %2d) vs (morituri: %02d)
    # HMSF is used to represent pre-gaps' duration
    def _framesToHMSF(self, frames):
        """Returns HMSF representation of the provided frames value"""

        f = frames % common.FRAMES_PER_SECOND
        frames -= f
        s = (frames / common.FRAMES_PER_SECOND) % 60
        frames -= s * 60
        m = frames / common.FRAMES_PER_SECOND / 60
        frames -= m * 60
        h = frames / common.FRAMES_PER_SECOND / 60 / 60
        return "%2d:%02d:%02d.%02d" % (h, m, s, f)

    def log(self, ripResult, epoch=time.time()):
        """Returns big str: logfile joined text lines"""

        lines = self.logRip(ripResult, epoch=epoch)
        return "\n".join(lines)

    def logRip(self, ripResult, epoch):
        """Returns lines list"""

        lines = []

        # Ripper version
        # ATM differs from EAC's typical log line
        lines.append("morituri version %s" % configure.version)
        lines.append("")

        # Rip date
        # ATM differs from EAC's typical log line
        date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(epoch)).strip()
        lines.append("morituri extraction logfile from %s" % date)
        lines.append("")

        # Artist / Album
        lines.append("%s / %s" % (ripResult.artist, ripResult.title))
        lines.append("")

        # Drive information
        # Missing information about "Adapter" (not relevant on *nix?)
        lines.append(
            "Used drive  : %s%s" % (
                ripResult.vendor, ripResult.model))
        lines.append("")

        # Rip settings
        lines.append("Read mode               : Secure")
        # Extra line (not included in EAC's logfiles)
        lines.append("Use cdparanoia mode     : Yes (cdparanoia %s)" % (
            ripResult.cdparanoiaVersion))
        defeat = "Unknown"
        if ripResult.cdparanoiaDefeatsCache is True:
            defeat = "Yes"
        if ripResult.cdparanoiaDefeatsCache is False:
            defeat = "No"
        lines.append("Defeat audio cache      : %s" % defeat)
        lines.append("Make use of C2 pointers : No")
        lines.append("")
        lines.append("Read offset correction                      : %d" %
                     ripResult.offset)
        # Currently unsupported by unpatched cdparanoia
        lines.append("Overread into Lead-In and Lead-Out          : No")
        lines.append("Fill up missing offset samples with silence : Yes")
        lines.append("Delete leading and trailing silent blocks   : No")
        lines.append("Null samples used in CRC calculations       : Yes")
        # Missing line "Used interface" (not relevant on *nix?)
        # Extra line (not included in EAC's logfiles)
        lines.append("Gap detection                               : "
                     "cdrdao version %s" % ripResult.cdrdaoVersion)
        lines.append("Gap handling                                : "
                     "Appended to previous track")
        lines.append("")

        # ATM differs from EAC's typical log line
        lines.append("Used output format       : %s" %
                     ripResult.profileName)
        # Extra lines (not included in EAC's logfiles)
        # Are these appropriate replacements of the following missing lines?
        # ("Selected bitrate", "Quality", "Add ID3 tag"
        # "Command line compressor", "Additional command line options")
        lines.append("GStreamer pipeline       : %s" %
                     ripResult.profilePipeline)
        lines.append("GStreamer version        : %s" %
                     ripResult.gstreamerVersion)
        lines.append("GStreamer Python version : %s" %
                     ripResult.gstPythonVersion)
        lines.append("Encoder plugin version   : %s" %
                     ripResult.encoderVersion)
        lines.append("")
        lines.append("")

        # TOC
        lines.append("TOC of the extracted CD")
        lines.append("")
        lines.append(
            "     Track |   Start  |  Length  | Start sector | End sector ")
        lines.append(
            "    ---------------------------------------------------------")
        table = ripResult.table

        htoa = None
        try:
            htoa = table.tracks[0].getIndex(0)
        except KeyError:
            pass

        # If true include HTOA line in log's TOC
        if htoa and htoa.path:
            htoastart = htoa.absolute
            htoaend = table.getTrackEnd(0)
            htoalength = table.tracks[0].getIndex(1).absolute - htoastart
            lines.append(
                "       %2d  | %s | %s |    %6d    |   %6d   " % (
                    0,
                    self._framesToMSF(htoastart),
                    self._framesToMSF(htoalength),
                    htoastart, htoaend))

        # For every track include information in the TOC
        for t in table.tracks:
            # FIXME: what happens to a track start over 60 minutes ?
            # Answer: tested empirically, everything seems OK
            start = t.getIndex(1).absolute
            length = table.getTrackLength(t.number)
            end = table.getTrackEnd(t.number)
            lines.append(
                "       %2d  | %s | %s |    %6d    |   %6d   " % (
                    t.number,
                    self._framesToMSF(start),
                    self._framesToMSF(length),
                    start, end))
        lines.append("")
        lines.append("")

        # AccurateRip summary at the end of the logfile
        if self._inARDatabase == 0:
            lines.append("None of the tracks are present "
                         "in the AccurateRip database")
        else:
            nonHTOA = len(ripResult.tracks)
            if ripResult.tracks[0].number == 0:
                nonHTOA -= 1
            if self._accuratelyRipped == 0:
                lines.append("No tracks could be verified as accurate")
                lines.append(
                    "You may have a different pressing "
                    "from the one(s) in the database")
            elif self._accuratelyRipped < nonHTOA:
                if self._accuratelyRipped < 10:
                    lines.append(" %d track(s) accurately ripped" %
                                 self._accuratelyRipped)
                else:
                    lines.append("%d track(s) accurately ripped" %
                                 self._accuratelyRipped)
                if (nonHTOA - self._accuratelyRipped) < 10:
                    lines.append(" %d track(s) could not be verified "
                                 "as accurate" %
                                 (nonHTOA - self._accuratelyRipped))
                else:
                    lines.append("%d track(s) could not be verified "
                                 "as accurate" %
                                 (nonHTOA - self._accuratelyRipped))
                lines.append("")
                lines.append("Some tracks could not be verified as accurate")
            else:
                lines.append("All tracks accurately ripped")
        lines.append("")

        # FIXME: ATM this will always pick else (when does EAC report errors)
        if self._errors:
            lines.append("There were errors")
        else:
            lines.append("No errors occurred")
        lines.append("")

        # END of ripper status report
        # in EAC this isn't always the second to last line in the log because
        # plugins information are included beneath (but before log checksum)
        lines.append("End of status report")
        lines.append("")

        # Log checksum (uppercase hex encoded SHA256 hash of all lines)
        # It isn't compatible with EAC's one: checklog fail
        hasher = hashlib.sha256()
        hasher.update("\n".join(lines).encode("utf-8"))
        lines.append("==== Log checksum %s ====" % hasher.hexdigest().upper())
        lines.append("")

        return lines

    def trackLog(self, trackResult):
        """Returns tracks section lines: data picked from trackResult"""

        lines = []

        # Track number (formatting like EAC's one)
        if trackResult.number < 10:
            lines.append("Track  %2d" % trackResult.number)
        else:
            lines.append("Track %2d" % trackResult.number)
        lines.append("")

        # Filename (including path) of ripped track
        lines.append("     Filename %s" % trackResult.filename)
        lines.append("")

        # Pre-gap length
        # EAC always adds 2 seconds to the first track pre-gap
        pregap = trackResult.pregap
        if trackResult.number == 1:
            pregap += 2 * common.FRAMES_PER_SECOND
        if pregap:
            lines.append("     Pre-gap length  %s" % self._framesToHMSF(
                pregap))
            lines.append("")

        # Peak level
        # EAC seems to format peak differently, truncating to the 3rd digit,
        # and also calculating it against a max of 32767
        # MBV - Feed me with your kiss: replaygain 0.809875,
        # EAC's peak level 80.9 % instead of 90.0 %
        peak = trackResult.peak * 32768 / 32767
        lines.append("     Peak level %.1f %%" % (
            int(peak * 1000) / 10.0))

        # Extraction speed
        if trackResult.copyspeed:
            lines.append("     Extraction speed %.1f X" % (
                trackResult.copyspeed))

        # Track quality
        if trackResult.quality and trackResult.quality > 0.001:
            lines.append("     Track quality %.1f %%" % (
                trackResult.quality * 100.0, ))

        # Ripper test CRC
        if trackResult.testcrc is not None:
            lines.append("     Test CRC %08X" % trackResult.testcrc)

        # Ripper copy CRC
        if trackResult.copycrc is not None:
            lines.append("     Copy CRC %08X" % trackResult.copycrc)

        # AccurateRip track status
        # ATM there's no support for AccurateRip V2
        if trackResult.accurip:
            self._inARDatabase += 1
            if trackResult.ARCRC == trackResult.ARDBCRC:
                lines.append(
                    "     Accurately ripped (confidence %d)  [%08X]  (AR v1)" %
                    (trackResult.ARDBConfidence, trackResult.ARCRC))
                self._accuratelyRipped += 1
            else:
                lines.append(
                    "     Cannot be verified as accurate  "
                    "(confidence %d),  [%08X], AccurateRip "
                    "returned [%08x]  (AR v1)" %
                    (trackResult.ARDBConfidence,
                     trackResult.ARCRC, trackResult.ARDBCRC))
        else:
            lines.append("     Track not present in AccurateRip database")

        # EAC emits 0 warnings even when a CRC mismatch occurs
        if trackResult.testcrc == trackResult.copycrc:
            lines.append("     Copy OK")
        return lines
