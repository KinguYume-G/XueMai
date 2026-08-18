import { ExternalLink, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

interface DigitalTwinSectionProps {
    buildingImage: string
    buildingName: string
    arQrCode?: string
    arUrl: string
}

export default function DigitalTwinSection({
    buildingImage,
    buildingName,
    arQrCode,
    arUrl,
}: DigitalTwinSectionProps) {
    return (
        <div className="px-6 py-16 bg-slate-900/50">
            <div className="max-w-7xl mx-auto">
                <h2 className="text-4xl font-bold text-white mb-4 text-center">
                    Digital Twin Campus
                </h2>
                <p className="text-gray-300 text-center mb-12 text-lg">
                    Experience our campus in immersive 3D and Augmented Reality
                </p>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                    {/* Left: Building Image */}
                    <div className="relative group">
                        <div className="relative rounded-3xl overflow-hidden shadow-2xl">
                            <img
                                src={buildingImage}
                                alt={buildingName}
                                className="w-full h-[500px] object-cover transition-transform duration-500 group-hover:scale-105"
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 to-transparent" />

                            {/* Interactive 3D Badge */}
                            <div className="absolute top-6 left-6 glass-card px-4 py-2 rounded-full flex items-center gap-2 text-white">
                                <Sparkles className="h-4 w-4 text-cyan-400" />
                                <span className="text-sm font-semibold">Interactive 3D</span>
                            </div>

                            <div className="absolute bottom-6 left-6 text-white">
                                <h3 className="text-2xl font-bold">{buildingName}</h3>
                                <p className="text-gray-300">Click to explore in 3D</p>
                            </div>
                        </div>
                    </div>

                    {/* Right: AR Experience Card */}
                    <div>
                        <Card className="bg-white rounded-3xl border-0 shadow-2xl hover:shadow-3xl transition-all duration-300">
                            <CardContent className="p-8">
                                <div className="flex items-center gap-3 mb-6">
                                    <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl">
                                        <Sparkles className="h-6 w-6 text-white" />
                                    </div>
                                    <div>
                                        <h3 className="text-2xl font-bold text-slate-900">
                                            AR Experience
                                        </h3>
                                        <p className="text-gray-600">
                                            Scan to view in your space
                                        </p>
                                    </div>
                                </div>

                                <div className="bg-slate-50 rounded-2xl p-6 mb-6">
                                    <p className="text-gray-700 mb-4">
                                        Use your smartphone to experience our campus in Augmented Reality.
                                        See buildings, facilities, and campus life in 3D overlaid on your environment.
                                    </p>

                                    {/* QR Code Placeholder */}
                                    <div className="bg-white border-2 border-dashed border-gray-300 rounded-xl p-6 flex items-center justify-center">
                                        {arQrCode ? (
                                            <img src={arQrCode} alt="AR Experience QR Code" className="w-40 h-40" />
                                        ) : (
                                            <div className="w-40 h-40 bg-gradient-to-br from-slate-200 to-slate-300 rounded-xl flex items-center justify-center">
                                                <div className="text-center">
                                                    <div className="text-4xl mb-2">📱</div>
                                                    <div className="text-xs text-gray-600">QR Code</div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <Button
                                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-6 text-lg rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300"
                                    onClick={() => window.open(arUrl, '_blank')}
                                >
                                    <ExternalLink className="mr-2 h-5 w-5" />
                                    Launch AR Experience
                                </Button>

                                <p className="text-xs text-gray-500 text-center mt-4">
                                    Requires smartphone with AR capability
                                </p>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    )
}
