import { Play, Video } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface CampusHeroProps {
    title: string
    subtitle: string
    backgroundImage: string
    statusInfo?: {
        location: string
        temperature: string
        status: string
    }
    onWatchVideo?: () => void
    onVRTour?: () => void
}

export default function CampusHero({
    title,
    subtitle,
    backgroundImage,
    statusInfo = { location: 'KL Campus', temperature: '32°C', status: 'Open' },
    onWatchVideo,
    onVRTour,
}: CampusHeroProps) {
    return (
        <div className="relative w-full h-[600px] overflow-hidden -mx-6 -mt-8">
            {/* Background Image with Overlay */}
            <div
                className="absolute inset-0 bg-cover bg-center"
                style={{ backgroundImage: `url(${backgroundImage})` }}
            >
                <div className="absolute inset-0 bg-gradient-to-br from-slate-950/90 via-slate-900/80 to-blue-950/90" />
            </div>

            {/* Status Capsule - Top Right */}
            {statusInfo && (
                <div className="absolute top-8 right-12 glass-card px-6 py-3 rounded-full flex items-center gap-3 text-white text-sm font-medium">
                    <span>{statusInfo.location}</span>
                    <span className="text-gray-300">•</span>
                    <span>{statusInfo.temperature}</span>
                    <span className="text-gray-300">•</span>
                    <span className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                        {statusInfo.status}
                    </span>
                </div>
            )}

            {/* Hero Content */}
            <div className="relative h-full flex flex-col items-center justify-center text-center px-6">
                <h1 className="text-6xl md:text-7xl font-bold mb-4 gradient-text">
                    {title}
                </h1>
                <p className="text-2xl md:text-3xl text-gray-200 mb-12 max-w-3xl">
                    {subtitle}
                </p>

                {/* Action Buttons */}
                <div className="flex flex-wrap gap-4 justify-center">
                    <Button
                        size="lg"
                        onClick={onWatchVideo}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-6 text-lg rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105"
                    >
                        <Play className="mr-2 h-5 w-5" />
                        Watch Campus Video
                    </Button>
                    <Button
                        size="lg"
                        variant="outline"
                        onClick={onVRTour}
                        className="bg-white/10 hover:bg-white/20 text-white border-white/30 px-8 py-6 text-lg rounded-2xl backdrop-blur-sm shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105"
                    >
                        <Video className="mr-2 h-5 w-5" />
                        VR Tour
                    </Button>
                </div>
            </div>
        </div>
    )
}
