using Microsoft.CognitiveServices.Speech;
using Microsoft.CognitiveServices.Speech.Audio;
using System;
using System.IO;
using System.Threading.Tasks;

class Program
{
    private static readonly string SubscriptionKey = "233lj2lkj1lkj2ghlj";
    private static readonly string Region = "eastus";
    private static readonly string AudioFile = "test.wav";
    private static readonly string OutputFile = "transcription.txt";

    static async Task Main(string[] args)
    {
        try
        {
            var speechConfig = SpeechConfig.FromSubscription(SubscriptionKey, Region);
            speechConfig.SpeechRecognitionLanguage = "en-US";
            using var audioConfig = AudioConfig.FromWavFileInput(AudioFile);
            using var speechRecognizer = new SpeechRecognizer(speechConfig, audioConfig);

            string transcriptionText = "";
            speechRecognizer.Recognized += (sender, e) =>
            {
                if (e.Result.Reason == ResultReason.RecognizedSpeech)
                {
                    transcriptionText += e.Result.Text + Environment.NewLine;
                    Console.WriteLine($"Recognized: {e.Result.Text}");
                }
            };

            await speechRecognizer.StartContinuousRecognitionAsync();
            Console.WriteLine("Press Enter to stop recognition...");
            Console.ReadLine();
            await speechRecognizer.StopContinuousRecognitionAsync();

            await File.WriteAllTextAsync(OutputFile, transcriptionText);
            Console.WriteLine($"Transcription saved to {OutputFile}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error occurred: {ex.Message}");
        }
    }
}
