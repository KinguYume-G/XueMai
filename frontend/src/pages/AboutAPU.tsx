import CampusHero from '@/components/campus/CampusHero'
import StatsCards from '@/components/campus/StatsCards'
import DigitalTwinSection from '@/components/campus/DigitalTwinSection'
import CampusActivityTabs from '@/components/campus/CampusActivityTabs'
import { Users, Globe, TrendingUp } from 'lucide-react'

// Public assets are served from the site root in both development and production.
const HERO_BG = '/logo.png'
const MASSE_HALL = '/logo.png'
const ACTIVITY_LIFE = '/ai.png'
const ACTIVITY_FOOD = '/ai.png'
const ACTIVITY_STUDY = '/ai.png'
const ACTIVITY_NEARBY = '/ai.png'

export default function AboutAPU() {
  const stats = [
    {
      icon: <Users className="h-12 w-12 text-blue-500" />,
      value: '12,000+',
      label: 'International Students',
    },
    {
      icon: <Globe className="h-12 w-12 text-purple-500" />,
      value: '130+',
      label: 'Countries Represented',
    },
    {
      icon: <TrendingUp className="h-12 w-12 text-cyan-500" />,
      value: '100%',
      label: 'Employability Rate',
    },
  ]

  const activities = {
    life: [
      {
        title: 'Student Hub',
        description: 'Modern collaborative spaces where students connect, network, and build lifelong friendships across cultures.',
        image: ACTIVITY_LIFE,
        tag: 'Community',
      },
      {
        title: 'Sports & Recreation',
        description: 'State-of-the-art facilities including basketball courts, fitness center, and outdoor sports areas.',
        image: ACTIVITY_LIFE,
        tag: 'Wellness',
      },
      {
        title: 'Cultural Events',
        description: 'Regular festivals celebrating diversity with international food fairs, performances, and cultural showcases.',
        image: ACTIVITY_LIFE,
        tag: 'Culture',
      },
    ],
    food: [
      {
        title: 'Main Cafeteria',
        description: 'Diverse food court offering Asian, Western, and Middle Eastern cuisine with halal-certified options.',
        image: ACTIVITY_FOOD,
        tag: 'Dining',
      },
      {
        title: 'Coffee Lounge',
        description: 'Modern café serving specialty coffee, fresh pastries, and quick bites for study sessions.',
        image: ACTIVITY_FOOD,
        tag: 'Café',
      },
      {
        title: 'Food Trucks',
        description: 'Rotating selection of local Malaysian street food and international cuisines throughout the week.',
        image: ACTIVITY_FOOD,
        tag: 'Street Food',
      },
    ],
    study: [
      {
        title: 'Digital Library',
        description: 'Modern library with over 50,000 books, digital resources, and quiet study zones with 24/7 access.',
        image: ACTIVITY_STUDY,
        tag: 'Library',
      },
      {
        title: 'Innovation Labs',
        description: 'Equipped with latest technology for software development, AI research, and cybersecurity projects.',
        image: ACTIVITY_STUDY,
        tag: 'Tech',
      },
      {
        title: 'Group Study Rooms',
        description: 'Bookable collaborative spaces with smart boards, video conferencing, and presentation equipment.',
        image: ACTIVITY_STUDY,
        tag: 'Collaboration',
      },
    ],
    nearby: [
      {
        title: 'KLCC & Petronas Towers',
        description: 'Just 15 minutes away - explore the iconic twin towers, shopping mall, and Symphony Lake.',
        image: ACTIVITY_NEARBY,
        tag: '15 min',
      },
      {
        title: 'Bukit Bintang',
        description: 'KL\'s entertainment district with shopping, dining, and nightlife - easily accessible by LRT.',
        image: ACTIVITY_NEARBY,
        tag: '20 min',
      },
      {
        title: 'Public Transport',
        description: 'Well-connected to Kuala Lumpur\'s LRT and MRT network for easy city exploration.',
        image: ACTIVITY_NEARBY,
        tag: 'Transit',
      },
    ],
  }

  const handleWatchVideo = () => {
    window.open('https://www.youtube.com/results?search_query=Asia+Pacific+University+Malaysia+campus+tour', '_blank', 'noopener,noreferrer')
  }

  const handleVRTour = () => {
    window.open('https://apu.edu.my/virtual-tour', '_blank')
  }

  return (
    <div className="min-h-screen bg-slate-950 -mx-6 -mt-8">
      {/* Hero Section */}
      <CampusHero
        title="Technology for Transformation"
        subtitle="Asia Pacific University of Technology & Innovation"
        backgroundImage={HERO_BG}
        statusInfo={{
          location: 'KL Campus',
          temperature: '32°C',
          status: 'Open',
        }}
        onWatchVideo={handleWatchVideo}
        onVRTour={handleVRTour}
      />

      {/* Stats Section */}
      <StatsCards stats={stats} />

      {/* Digital Twin Section */}
      <DigitalTwinSection
        buildingImage={MASSE_HALL}
        buildingName="Masse Hall"
        arUrl="https://apu.edu.my/ar-experience"
      />

      {/* Campus Activities */}
      <CampusActivityTabs activities={activities} />

      {/* Footer Section */}
      <div className="px-6 py-16 bg-slate-900">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-12">
          {/* Mission */}
          <div>
            <h3 className="text-2xl font-bold text-white mb-4">Our Mission</h3>
            <p className="text-gray-300 leading-relaxed">
              To nurture professionals with global perspective, innovative mindset, and practical skills.
              We cultivate high-end technology and management talent for the Asia-Pacific region through
              quality education and international learning environments.
            </p>
          </div>

          {/* Vision */}
          <div>
            <h3 className="text-2xl font-bold text-white mb-4">Our Vision</h3>
            <p className="text-gray-300 leading-relaxed">
              To become the leading technology university in the Asia-Pacific region, renowned internationally
              in computer science, engineering, and business management, driving educational innovation and
              preparing future-ready graduates.
            </p>
          </div>

          {/* Quick Facts */}
          <div>
            <h3 className="text-2xl font-bold text-white mb-4">Quick Facts</h3>
            <div className="space-y-3 text-gray-300">
              <div className="flex justify-between">
                <span className="font-medium">Founded:</span>
                <span>1993</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium">Location:</span>
                <span>Kuala Lumpur, Malaysia</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium">Campus Size:</span>
                <span>23 Acres</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium">Type:</span>
                <span>Private University</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium">Global Ranking:</span>
                <span>Top 2% Worldwide</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Credits */}
        <div className="mt-12 pt-8 border-t border-slate-700 text-center text-gray-400">
          <p>© 2024 Asia Pacific University of Technology & Innovation. All rights reserved.</p>
        </div>
      </div>
    </div>
  )
}
