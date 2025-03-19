import React, { useState, useEffect } from 'react';
import { NextPage } from 'next';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import { FiUpload, FiType, FiLayers, FiImage, FiDownload, FiMenu, FiX } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';

const Home: NextPage = () => {
  const router = useRouter();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleGetStarted = () => {
    console.log('Navigating to upload page...');
    // Use both methods for redundancy
    router.push('/upload').catch(err => {
      console.error('Router navigation failed, using fallback:', err);
      window.location.href = '/upload';
    });
  };

  const fadeUpVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: {
        duration: 1,
        delay: 0.5 + i * 0.2,
        ease: [0.25, 0.4, 0.25, 1],
      },
    }),
  };

  return (
    <div className="min-h-screen bg-[#030303] text-white">
      <Head>
        <title>ProCaptions - AI-Powered Image Text Editor</title>
        <meta name="description" content="Transform your images with stunning dynamic text overlays using ProCaptions" />
      </Head>

      {/* Navigation */}
      <motion.header
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled ? "bg-black/30 backdrop-blur-lg border-b border-white/10 py-3" : "bg-transparent py-5"
        }`}
      >
        <div className="container mx-auto px-4 md:px-6">
          <div className="flex items-center justify-between">
            <Link href="/" className="text-white font-bold text-xl">
              ProCaptions
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-white/80 hover:text-white transition-colors">
                Features
              </a>
              <a href="#how-it-works" className="text-white/80 hover:text-white transition-colors">
                How It Works
              </a>
              <a href="#examples" className="text-white/80 hover:text-white transition-colors">
                Examples
              </a>
            </nav>

            <div className="hidden md:flex items-center space-x-4">
              <button
                onClick={handleGetStarted}
                className="bg-gradient-to-r from-indigo-500 to-rose-500 hover:opacity-90 transition-opacity px-5 py-2 rounded-md"
              >
                Get Started
              </button>
            </div>

            {/* Mobile Menu Button */}
            <button className="md:hidden text-white" onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
              {isMobileMenuOpen ? <FiX size={24} /> : <FiMenu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden bg-black/80 backdrop-blur-lg border-b border-white/10"
            >
              <div className="container mx-auto px-4 py-4">
                <nav className="flex flex-col space-y-4">
                  <a
                    href="#features"
                    className="text-white/80 hover:text-white transition-colors py-2"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Features
                  </a>
                  <a
                    href="#how-it-works"
                    className="text-white/80 hover:text-white transition-colors py-2"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    How It Works
                  </a>
                  <a
                    href="#examples"
                    className="text-white/80 hover:text-white transition-colors py-2"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Examples
                  </a>
                  <div className="pt-2">
                    <button
                      onClick={handleGetStarted}
                      className="bg-gradient-to-r from-indigo-500 to-rose-500 hover:opacity-90 transition-opacity w-full px-5 py-2 rounded-md"
                    >
                      Get Started
                    </button>
                  </div>
                </nav>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.header>

      {/* Hero Section */}
      <div className="relative min-h-screen w-full flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/[0.05] via-transparent to-rose-500/[0.05] blur-3xl" />

        {/* Animated shapes */}
        <div className="absolute inset-0 overflow-hidden">
          <motion.div
            initial={{ opacity: 0, y: -150, rotate: -15 }}
            animate={{ opacity: 1, y: 0, rotate: 12 }}
            transition={{ duration: 2.4, delay: 0.3, ease: [0.23, 0.86, 0.39, 0.96] }}
            className="absolute left-[-10%] md:left-[-5%] top-[15%] md:top-[20%]"
          >
            <motion.div
              animate={{ y: [0, 15, 0] }}
              transition={{ duration: 12, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
              style={{ width: 600, height: 140 }}
              className="relative"
            >
              <div className="absolute inset-0 rounded-full bg-gradient-to-r from-indigo-500/[0.15] to-transparent backdrop-blur-[2px] border-2 border-white/[0.15] shadow-[0_8px_32px_0_rgba(255,255,255,0.1)] after:absolute after:inset-0 after:rounded-full after:bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.2),transparent_70%)]" />
            </motion.div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: -150, rotate: 0 }}
            animate={{ opacity: 1, y: 0, rotate: -15 }}
            transition={{ duration: 2.4, delay: 0.5, ease: [0.23, 0.86, 0.39, 0.96] }}
            className="absolute right-[-5%] md:right-[0%] top-[70%] md:top-[75%]"
          >
            <motion.div
              animate={{ y: [0, 15, 0] }}
              transition={{ duration: 12, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
              style={{ width: 500, height: 120 }}
              className="relative"
            >
              <div className="absolute inset-0 rounded-full bg-gradient-to-r from-rose-500/[0.15] to-transparent backdrop-blur-[2px] border-2 border-white/[0.15] shadow-[0_8px_32px_0_rgba(255,255,255,0.1)] after:absolute after:inset-0 after:rounded-full after:bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.2),transparent_70%)]" />
            </motion.div>
          </motion.div>
        </div>

        <div className="relative z-10 container mx-auto px-4 md:px-6 pt-20">
          <div className="max-w-3xl mx-auto text-center">
            <motion.div
              custom={0}
              variants={fadeUpVariants}
              initial="hidden"
              animate="visible"
              className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.03] border border-white/[0.08] mb-8 md:mb-12"
            >
              <div className="w-5 h-5 rounded-full bg-gradient-to-r from-indigo-500 to-rose-500" />
              <span className="text-sm text-white/60 tracking-wide">ProCaptions</span>
            </motion.div>

            <motion.div custom={1} variants={fadeUpVariants} initial="hidden" animate="visible">
              <h1 className="text-4xl sm:text-6xl md:text-7xl font-bold mb-6 md:mb-8 tracking-tight">
                <span className="bg-clip-text text-transparent bg-gradient-to-b from-white to-white/80">AI-Powered</span>
                <br />
                <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 via-white/90 to-rose-300">
                  Image Text Editor
                </span>
              </h1>
            </motion.div>

            <motion.div custom={2} variants={fadeUpVariants} initial="hidden" animate="visible">
              <p className="text-base sm:text-lg md:text-xl text-white/40 mb-8 leading-relaxed font-light tracking-wide max-w-2xl mx-auto px-4">
                Transform your images into professional poster-style designs with ease. Add beautiful text effects behind your subjects with just a few clicks.
              </p>
            </motion.div>

            <motion.div custom={3} variants={fadeUpVariants} initial="hidden" animate="visible">
              <button
                onClick={handleGetStarted}
                className="bg-gradient-to-r from-indigo-500 to-rose-500 hover:opacity-90 transition-opacity text-white px-8 py-6 text-lg rounded-full shadow-lg shadow-indigo-500/20"
              >
                Try ProCaptions Now
              </button>
            </motion.div>
          </div>
        </div>

        <div className="absolute inset-0 bg-gradient-to-t from-[#030303] via-transparent to-[#030303]/80 pointer-events-none" />
      </div>

      {/* Features Section */}
      <section id="features" className="py-24 relative">
        <div className="container mx-auto px-4 md:px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 to-rose-300">
              Key Features
            </h2>
            <p className="text-white/40 max-w-2xl mx-auto">
              ProCaptions offers powerful features to help you create stunning visual content.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              viewport={{ once: true }}
              className="bg-white/[0.03] backdrop-blur-sm border border-white/10 rounded-xl p-6"
            >
              <div className="bg-gradient-to-br from-indigo-500 to-indigo-600 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <FiImage className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-2">AI-Powered Subject Isolation</h3>
              <p className="text-white/40">Automatically separates the foreground subject from the background using advanced AI.</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              viewport={{ once: true }}
              className="bg-white/[0.03] backdrop-blur-sm border border-white/10 rounded-xl p-6"
            >
              <div className="bg-gradient-to-br from-rose-500 to-rose-600 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <FiType className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Dramatic Text Effects</h3>
              <p className="text-white/40">Create eye-catching text effects with customizable fonts, sizes, and styles.</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              viewport={{ once: true }}
              className="bg-white/[0.03] backdrop-blur-sm border border-white/10 rounded-xl p-6"
            >
              <div className="bg-gradient-to-br from-purple-500 to-purple-600 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <FiLayers className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Multi-Layer Text Editing</h3>
              <p className="text-white/40">Add multiple text layers with different styles, positions, and effects.</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              viewport={{ once: true }}
              className="bg-white/[0.03] backdrop-blur-sm border border-white/10 rounded-xl p-6"
            >
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <FiUpload className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Easy Upload Process</h3>
              <p className="text-white/40">Simple drag-and-drop interface for quick image uploads and processing.</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.5 }}
              viewport={{ once: true }}
              className="bg-white/[0.03] backdrop-blur-sm border border-white/10 rounded-xl p-6"
            >
              <div className="bg-gradient-to-br from-green-500 to-green-600 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <FiDownload className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-2">High-Quality Exports</h3>
              <p className="text-white/40">Download your creations in high resolution, ready for social media or printing.</p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-24 relative bg-gradient-to-b from-transparent to-black/40">
        <div className="container mx-auto px-4 md:px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 to-rose-300">
              How It Works
            </h2>
            <p className="text-white/40 max-w-2xl mx-auto">
              Creating captivating images with ProCaptions is simple and fast.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              viewport={{ once: true }}
              className="flex flex-col items-center text-center"
            >
              <div className="bg-gradient-to-br from-indigo-500 to-rose-500 w-16 h-16 rounded-full flex items-center justify-center mb-4 text-white font-bold text-xl">
                1
              </div>
              <h3 className="text-xl font-semibold mb-2">Upload Your Image</h3>
              <p className="text-white/40">
                Upload any image with a clear subject. Our AI automatically isolates the foreground from the background.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              viewport={{ once: true }}
              className="flex flex-col items-center text-center"
            >
              <div className="bg-gradient-to-br from-indigo-500 to-rose-500 w-16 h-16 rounded-full flex items-center justify-center mb-4 text-white font-bold text-xl">
                2
              </div>
              <h3 className="text-xl font-semibold mb-2">Add Your Text</h3>
              <p className="text-white/40">
                Customize your text with different fonts, sizes, and styles. Position it exactly where you want it to appear.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              viewport={{ once: true }}
              className="flex flex-col items-center text-center"
            >
              <div className="bg-gradient-to-br from-indigo-500 to-rose-500 w-16 h-16 rounded-full flex items-center justify-center mb-4 text-white font-bold text-xl">
                3
              </div>
              <h3 className="text-xl font-semibold mb-2">Download Your Creation</h3>
              <p className="text-white/40">
                Preview your final image with text behind the subject and download it in high resolution.
              </p>
            </motion.div>
          </div>

          <div className="text-center mt-12">
            <motion.button
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
              onClick={handleGetStarted}
              className="bg-gradient-to-r from-indigo-500 to-rose-500 hover:opacity-90 transition-opacity text-white px-6 py-3 rounded-lg shadow-lg shadow-indigo-500/20"
            >
              Get Started Now
            </motion.button>
          </div>
        </div>
      </section>

      {/* Examples Section */}
      <section id="examples" className="py-24 relative">
        <div className="container mx-auto px-4 md:px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 to-rose-300">
              See It In Action
            </h2>
            <p className="text-white/40 max-w-2xl mx-auto">
              Check out some examples of what you can create with ProCaptions.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[1, 2, 3].map((item) => (
              <motion.div 
                key={item}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: item * 0.1 }}
                viewport={{ once: true }}
                className="bg-white/[0.03] backdrop-blur-sm border border-white/10 rounded-xl overflow-hidden"
              >
                <div className="aspect-video bg-gradient-to-br from-indigo-900/30 to-rose-900/30 flex items-center justify-center">
                  <div className="text-xl text-white/50">Example Image {item}</div>
                </div>
                <div className="p-4">
                  <h3 className="text-lg font-medium mb-1">Design Style {item}</h3>
                  <p className="text-white/40 text-sm">Create professional poster designs effortlessly</p>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="text-center mt-12">
            <motion.button
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
              onClick={handleGetStarted}
              className="bg-gradient-to-r from-indigo-500 to-rose-500 hover:opacity-90 transition-opacity text-white px-6 py-3 rounded-lg shadow-lg shadow-indigo-500/20"
            >
              Create Your Own
            </motion.button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative">
        <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/10 to-rose-500/10 blur-3xl" />
        <div className="container mx-auto px-4 md:px-6 relative z-10">
          <div className="max-w-4xl mx-auto bg-white/[0.03] backdrop-blur-sm border border-white/10 rounded-xl p-8 md:p-12 text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 to-rose-300">
              Ready to Transform Your Images?
            </h2>
            <p className="text-white/40 mb-8 max-w-2xl mx-auto">
              Join thousands of creators who use ProCaptions to make stunning images with professional text effects.
            </p>
            <button
              onClick={handleGetStarted}
              className="bg-gradient-to-r from-indigo-500 to-rose-500 hover:opacity-90 transition-opacity text-white px-8 py-4 rounded-lg shadow-lg shadow-indigo-500/20 text-lg"
            >
              Start Creating Now
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-white/10">
        <div className="container mx-auto px-4 md:px-6">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="mb-6 md:mb-0">
              <Link href="/" className="text-white font-bold text-xl">
                ProCaptions
              </Link>
              <p className="text-white/40 mt-2">Transform your images with AI-powered text effects</p>
            </div>
            <div className="flex flex-col md:flex-row items-center space-y-4 md:space-y-0 md:space-x-8">
              <a href="#features" className="text-white/60 hover:text-white transition-colors">
                Features
              </a>
              <a href="#how-it-works" className="text-white/60 hover:text-white transition-colors">
                How It Works
              </a>
              <button
                onClick={handleGetStarted}
                className="bg-gradient-to-r from-indigo-500 to-rose-500 hover:opacity-90 transition-opacity text-white px-5 py-2 rounded-md"
              >
                Get Started
              </button>
            </div>
          </div>
          <div className="text-center mt-8 text-white/40 text-sm">
            &copy; {new Date().getFullYear()} ProCaptions. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home; 