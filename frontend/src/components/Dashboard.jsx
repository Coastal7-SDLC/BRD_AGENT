import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Brain, Download, FileText, CheckCircle, AlertCircle, Zap, Upload, X } from 'lucide-react'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import { marked } from 'marked'

const Dashboard = () => {
  const [projectDescription, setProjectDescription] = useState('')
  const [additionalInfo, setAdditionalInfo] = useState('')
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false)
  const [isProcessingFiles, setIsProcessingFiles] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  


  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files)
    processFiles(files)
    event.target.value = '' // Reset input
  }

  const processFiles = (files) => {
    // Configuration constants (should match backend config)
    const VALID_FILE_TYPES = ['application/pdf', 'text/markdown', 'text/x-markdown', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
    const MAX_FILES_COUNT = 10
    
    const validFiles = files.filter(file => {
      if (!VALID_FILE_TYPES.includes(file.type)) {
        console.warn(`File ${file.name} has unsupported type: ${file.type}`)
        return false
      }
      
      if (file.size > MAX_FILE_SIZE) {
        console.warn(`File ${file.name} is too large: ${(file.size / 1024 / 1024).toFixed(2)}MB`)
        return false
      }
      
      return true
    })

    if (validFiles.length !== files.length) {
      const rejectedCount = files.length - validFiles.length
      alert(`${rejectedCount} file(s) were rejected. Only PDF, MD, and DOCX files under 10MB are allowed.`)
    }

    if (validFiles.length === 0) return

    // Check if adding these files would exceed the limit
    if (uploadedFiles.length + validFiles.length > MAX_FILES_COUNT) {
      const canAdd = MAX_FILES_COUNT - uploadedFiles.length
      if (canAdd > 0) {
        alert(`Only ${canAdd} more file(s) can be added. Maximum ${MAX_FILES_COUNT} files allowed.`)
        validFiles.splice(canAdd) // Limit to what can be added
      } else {
        alert(`Maximum ${MAX_FILES_COUNT} files already uploaded. Please remove some files first.`)
        return
      }
    }

    const newFiles = validFiles.map(file => ({
      id: Date.now() + Math.random(),
      file: file,
      name: file.name,
      size: file.size,
      type: file.type
    }))

    setUploadedFiles(prev => [...prev, ...newFiles])
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.currentTarget.classList.add('border-blue-400', 'bg-blue-50')
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.currentTarget.classList.remove('border-blue-400', 'bg-blue-50')
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.currentTarget.classList.remove('border-blue-400', 'bg-blue-50')
    
    const files = Array.from(e.dataTransfer.files)
    processFiles(files)
  }

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId))
  }

  const readFileContent = async (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      
      if (file.type === 'application/pdf') {
        // For PDFs, we'll provide a placeholder since client-side PDF parsing is complex
        resolve(`[PDF Document: ${file.name}]\n\nThis is a PDF document. The content will be processed on the server side for better text extraction and analysis.`)
      } else if (file.type.includes('markdown') || file.type.includes('text')) {
        // For markdown and text files, read the actual content
        reader.onload = function(e) {
          const content = e.target.result
          // Limit content length to prevent excessive data transfer
          if (content.length > 50000) {
            resolve(content.substring(0, 50000) + '\n\n[Content truncated due to length]')
          } else {
            resolve(content)
          }
        }
        reader.readAsText(file)
      } else if (file.type.includes('wordprocessingml')) {
        // For DOCX files, provide a placeholder
        resolve(`[DOCX Document: ${file.name}]\n\nThis is a Word document. The content will be processed on the server side for better text extraction and analysis.`)
      } else {
        resolve(`[Unsupported file type: ${file.type}]`)
      }
      
      reader.onerror = () => reject(new Error('Failed to read file'))
    })
  }

  const generateBRD = async () => {
    setIsGenerating(true)
    setError(null)
    
    try {
      // Check if user has uploaded existing BRD documents
      const hasExistingBRD = uploadedFiles.some(file => 
        file.name.toLowerCase().includes('brd') || 
        file.name.toLowerCase().includes('business requirements') ||
        file.name.toLowerCase().includes('requirements document')
      )
      
      // Process files first
      if (uploadedFiles.length > 0) {
        setIsProcessingFiles(true)
        const fileContents = await Promise.all(
          uploadedFiles.map(async (fileObj) => {
            const content = await readFileContent(fileObj.file)
            return {
              filename: fileObj.name,
              content: content,
              type: fileObj.type
            }
          })
        )
        setIsProcessingFiles(false)
        
        // If user uploaded existing BRD documents, use the generate_brd_with_files endpoint
        // The backend will automatically detect and improve existing BRD documents
        if (hasExistingBRD) {
          const response = await fetch('/api/generate_brd_with_files', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              project_description: additionalInfo || 'Improve existing BRD document',
              uploaded_files: fileContents,
              model: 'gemini-2.0-flash'
            })
          })
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
          
          const data = await response.json()
          setResult(data)
        } else {
          // Generate BRD with supporting files
          const response = await fetch('/api/generate_brd_with_files', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              project_description: projectDescription || additionalInfo || 'Project requirements from uploaded files',
              uploaded_files: fileContents,
              model: 'gemini-2.0-flash'
            })
          })
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
          
          const data = await response.json()
          setResult(data)
        }
      } else {
        // Generate BRD from text input only
        const response = await fetch('/api/generate_brd_from_input', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            project_description: projectDescription || additionalInfo || 'Project requirements',
            model: 'gemini-2.0-flash'
          })
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        setResult(data)
      }
    } catch (err) {
      setError(err.message || 'Failed to generate BRD')
    } finally {
      setIsGenerating(false)
    }
  }



  const downloadBRD = () => {
    if (!result) return
    
    const element = document.createElement('a')
    const file = new Blob([result.brd_markdown], { type: 'text/markdown' })
    element.href = URL.createObjectURL(file)
    element.download = `${result.project_name.replace(/\s+/g, '_')}_BRD.md`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  const downloadPDF = async () => {
    if (!result) return
    
    setIsGeneratingPDF(true)
    
    try {
      // Configure marked for better PDF output
      marked.setOptions({
        breaks: true,
        gfm: true
      })
      
      // Convert markdown to HTML
      let htmlContent = marked(result.brd_markdown)
      
      // Enhance HTML with better styling for PDF
      htmlContent = htmlContent
        .replace(/<h1/g, '<h1 style="color: #1f2937; font-size: 18px; margin: 20px 0 10px 0; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px;"')
        .replace(/<h2/g, '<h2 style="color: #374151; font-size: 16px; margin: 18px 0 8px 0; font-weight: bold;"')
        .replace(/<h3/g, '<h3 style="color: #4b5563; font-size: 14px; margin: 16px 0 6px 0; font-weight: bold;"')
        .replace(/<ul/g, '<ul style="margin: 10px 0; padding-left: 20px;"')
        .replace(/<li/g, '<li style="margin: 5px 0;"')
        .replace(/<p/g, '<p style="margin: 8px 0;"')
        .replace(/<strong/g, '<strong style="font-weight: bold;"')
        .replace(/<em/g, '<em style="font-style: italic;"')
      
      // Create a temporary container for the content
      const tempContainer = document.createElement('div')
      tempContainer.style.position = 'absolute'
      tempContainer.style.left = '-9999px'
      tempContainer.style.top = '0'
      tempContainer.style.width = '800px'
      tempContainer.style.padding = '40px'
      tempContainer.style.backgroundColor = 'white'
      tempContainer.style.fontFamily = 'Arial, sans-serif'
      tempContainer.style.fontSize = '12px'
      tempContainer.style.lineHeight = '1.6'
      tempContainer.style.color = '#333'
      tempContainer.style.boxShadow = '0 0 10px rgba(0,0,0,0.1)'
      tempContainer.style.borderRadius = '8px'
      
      // Add the content with proper styling
      tempContainer.innerHTML = `
        <div style="text-align: center; margin-bottom: 30px;">
          <h1 style="color: #1f2937; font-size: 24px; margin-bottom: 10px; border-bottom: 2px solid #3b82f6; padding-bottom: 10px;">
            Business Requirements Document (BRD)
          </h1>
          <h2 style="color: #374151; font-size: 20px; margin: 0;">
            ${result.project_name}
          </h2>
          <p style="color: #6b7280; font-size: 14px; margin: 10px 0 0 0;">
            Generated on ${new Date().toLocaleDateString()}
          </p>
        </div>
        <div style="text-align: left; font-size: 12px; line-height: 1.6;">
          ${htmlContent}
        </div>
      `
      
      // Add to DOM temporarily
      document.body.appendChild(tempContainer)
      
      // Convert to canvas
      const canvas = await html2canvas(tempContainer, {
        scale: 3, // Higher scale for better quality
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff',
        width: 800,
        height: tempContainer.scrollHeight,
        logging: false,
        removeContainer: true
      })
      
      // Remove temporary container
      document.body.removeChild(tempContainer)
      
      // Create PDF
      const pdf = new jsPDF('p', 'mm', 'a4')
      const imgWidth = 210 // A4 width in mm
      const pageHeight = 295 // A4 height in mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width
      let heightLeft = imgHeight
      let position = 0
      
      // Add first page
      pdf.addImage(canvas, 'JPEG', 0, position, imgWidth, imgHeight)
      heightLeft -= pageHeight
      
      // Add additional pages if needed
      while (heightLeft >= 0) {
        position = heightLeft - imgHeight
        pdf.addPage()
        pdf.addImage(canvas, 'JPEG', 0, position, imgWidth, imgHeight)
        heightLeft -= pageHeight
      }
      
      // Save the PDF
      pdf.save(`${result.project_name.replace(/\s+/g, '_')}_BRD.pdf`)
      
    } catch (error) {
      console.error('Error generating PDF:', error)
      alert('Error generating PDF. Please try again.')
    } finally {
      setIsGeneratingPDF(false)
    }
  }

  const getFileIcon = (fileType) => {
    if (fileType === 'application/pdf') {
      return '📄'
    } else if (fileType.includes('markdown') || fileType.includes('text')) {
      return '📝'
    } else if (fileType.includes('wordprocessingml')) {
      return '📘'
    }
    return '📁'
  }

  const getFileTypeLabel = (fileType) => {
    if (fileType === 'application/pdf') {
      return 'PDF'
    } else if (fileType.includes('markdown') || fileType.includes('text')) {
      return 'Markdown'
    } else if (fileType.includes('wordprocessingml')) {
      return 'DOCX'
    }
    return 'Unknown'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <div className="container mx-auto px-3 sm:px-4 py-4 sm:py-6 lg:py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-4xl lg:max-w-5xl mx-auto space-y-4 sm:space-y-6 lg:space-y-8"
        >
          {/* Header */}
          <div className="text-center mb-6 sm:mb-8">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 mb-2 sm:mb-3">
              🚀 BRD Agent
            </h1>
            <p className="text-sm sm:text-base lg:text-lg text-gray-600 max-w-2xl mx-auto">
              AI-Powered Business Requirements Document Generator with Google Gemini Integration
            </p>
          </div>

          

        {/* Unified BRD Interface */}
        <div className="space-y-4 sm:space-y-6">
              {/* 1. Project Description Section */}
              <div>
                <label className="block text-sm sm:text-base font-semibold text-gray-800 mb-2 sm:mb-3 flex items-center">
                  <Brain className="h-4 w-4 sm:h-5 sm:w-5 text-purple-600 mr-2" />
                  Project Description Section
                </label>
                <div className="relative">
                  <textarea
                    value={projectDescription}
                    onChange={(e) => setProjectDescription(e.target.value)}
                    placeholder="Describe your project requirements in detail... Include features, stakeholders, business objectives, success criteria, constraints, and any specific needs. Be as detailed as possible to generate a comprehensive BRD."
                    className="input-field min-h-[150px] sm:min-h-[200px] resize-vertical text-xs sm:text-sm lg:text-base leading-relaxed border-2 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-200"
                    rows={8}
                  />
                  <div className="absolute bottom-2 right-2 sm:bottom-3 sm:right-3 text-xs text-gray-400">
                    {projectDescription.length} characters
                  </div>
                </div>
              </div>

              {/* 2. Additional Information */}
              <div>
                <label className="block text-sm sm:text-base font-semibold text-gray-800 mb-2 sm:mb-3 flex items-center">
                  <Brain className="h-4 w-4 sm:h-5 sm:w-5 text-purple-600 mr-2" />
                  Additional Information
                </label>
                <div className="relative">
                  <textarea
                    value={additionalInfo}
                    onChange={(e) => setAdditionalInfo(e.target.value)}
                    placeholder="Add any additional information, context, or specific requirements that might help in generating a more comprehensive BRD. This could include technical constraints, timeline information, budget considerations, or any other relevant details. If you're uploading an existing BRD document, you can add notes about what improvements you'd like to see."
                    className="input-field min-h-[120px] sm:min-h-[150px] resize-vertical text-xs sm:text-sm lg:text-base leading-relaxed border-2 focus:border-purple-500 focus:ring-4 focus:ring-purple-100 transition-all duration-200"
                    rows={4}
                  />
                </div>
              </div>

                              {/* 3. File Upload Section */}
                <div>
                  <label className="block text-sm font-semibold text-gray-800 mb-2 flex items-center">
                    <Upload className="h-4 w-4 text-blue-600 mr-2" />
                    Supporting Documents (Optional)
                  </label>
                  <div 
                    className="border-2 border-dashed border-gray-300 rounded-lg p-3 hover:border-blue-400 transition-colors duration-200"
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                  >
                    <div className="text-center">
                      <Upload className="mx-auto h-6 w-6 text-gray-400 mb-2" />
                      <p className="text-xs text-gray-600 mb-1">
                        Drop files here or click to browse
                      </p>
                      <p className="text-xs text-gray-500 mb-2">
                        PDF, MD, DOCX (Max 10MB)
                      </p>
                      <p className="text-xs text-blue-600 mb-2 font-medium">
                        💡 Upload BRD docs to improve or supporting docs to enhance
                      </p>
                      <input
                        type="file"
                        multiple
                        accept=".pdf,.md,.docx"
                        onChange={handleFileUpload}
                        className="hidden"
                        id="file-upload"
                      />
                      <label
                        htmlFor="file-upload"
                        className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 cursor-pointer transition-colors duration-200"
                      >
                        Choose Files
                      </label>
                    </div>
                  </div>
                
                {/* File List */}
                {uploadedFiles.length > 0 && (
                  <div className="mt-3 space-y-3">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-700">Uploaded Files:</p>
                      {isProcessingFiles && (
                        <div className="flex items-center space-x-2 text-xs text-blue-600">
                          <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-600"></div>
                          <span>Processing...</span>
                        </div>
                      )}
                    </div>
                    
                    {/* File Summary */}
                    <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
                      <div className="flex items-center justify-between text-xs text-blue-800">
                        <span>📊 Summary: {uploadedFiles.length} file(s) ready for processing</span>
                        <span className="font-medium">
                          Total: {uploadedFiles.reduce((acc, file) => acc + file.size, 0) / 1024 / 1024 < 1 
                            ? `${(uploadedFiles.reduce((acc, file) => acc + file.size, 0) / 1024).toFixed(1)} KB`
                            : `${(uploadedFiles.reduce((acc, file) => acc + file.size, 0) / 1024 / 1024).toFixed(2)} MB`
                          }
                        </span>
                      </div>
                    </div>
                    
                    {uploadedFiles.map((fileObj) => (
                      <div key={fileObj.id} className="flex items-center justify-between bg-gray-50 rounded-lg px-3 py-2 border border-gray-200">
                        <div className="flex items-center space-x-2">
                          <span className="text-lg">{getFileIcon(fileObj.type)}</span>
                          <div className="flex flex-col">
                            <span className="text-sm text-gray-700 font-medium">{fileObj.name}</span>
                            <div className="flex items-center space-x-2 text-xs text-gray-500">
                              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
                                {getFileTypeLabel(fileObj.type)}
                              </span>
                              <span>{(fileObj.size / 1024 / 1024).toFixed(2)} MB</span>
                            </div>
                          </div>
                        </div>
                        <button
                          onClick={() => removeFile(fileObj.id)}
                          className="text-red-500 hover:text-red-700 transition-colors duration-200 p-1 rounded-full hover:bg-red-50"
                          disabled={isProcessingFiles}
                          title="Remove file"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* 4. Generate Button */}
              <div className="pt-2 sm:pt-3">
                <button
                  onClick={generateBRD}
                  disabled={isGenerating || isProcessingFiles || (!projectDescription.trim() && !additionalInfo.trim() && uploadedFiles.length === 0)}
                  className="w-full py-2.5 sm:py-3 px-4 sm:px-6 text-sm sm:text-base lg:text-lg font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-500 rounded-lg sm:rounded-xl shadow-lg hover:shadow-xl transform hover:scale-[1.02] transition-all duration-200 disabled:transform-none disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  {isGenerating ? (
                    <div className="flex items-center justify-center space-x-2 sm:space-x-3">
                      <div className="animate-spin rounded-full h-3 w-3 sm:h-4 sm:w-4 lg:h-5 lg:w-5 border-b-2 border-white"></div>
                      <span>Generating BRD...</span>
                    </div>
                  ) : isProcessingFiles ? (
                    <div className="flex items-center justify-center space-x-2 sm:space-x-3">
                      <div className="animate-spin rounded-full h-3 w-3 sm:h-4 sm:w-4 lg:h-5 lg:w-5 border-b-2 border-white"></div>
                      <span>Processing Files...</span>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center space-x-2 sm:space-x-3">
                      <span>🚀 {uploadedFiles.some(file => 
                        file.name.toLowerCase().includes('brd') || 
                        file.name.toLowerCase().includes('business requirements') ||
                        file.name.toLowerCase().includes('requirements document')
                      ) ? 'Improve BRD Document' : 'Generate BRD Document'}</span>
                    </div>
                  )}
                </button>
              </div>
            </div>

          {/* Enhanced Error Display */}
          {error && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card bg-red-50 border-red-200 shadow-lg"
            >
              <div className="flex items-center space-x-2 sm:space-x-3">
                <AlertCircle className="h-4 w-4 sm:h-5 sm:w-5 text-red-600" />
                <span className="text-xs sm:text-sm lg:text-base text-red-800 font-medium">Error: {error}</span>
              </div>
            </motion.div>
          )}

          {/* Enhanced Results Display */}
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="space-y-4 sm:space-y-6"
            >
              {/* Success Message */}
              <div className="card bg-gradient-to-r from-green-50 to-emerald-50 border-green-200 shadow-lg">
                <div className="flex items-center space-x-2 sm:space-x-3">
                  <CheckCircle className="h-4 w-4 sm:h-5 sm:w-5 text-green-600" />
                  <span className="text-xs sm:text-sm lg:text-base text-green-800 font-medium">{result.message}</span>
                </div>
              </div>

              {/* File Processing Summary */}
              {result.summary && result.summary.files_processed > 0 && (
                <div className="card shadow-lg bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
                  <h3 className="text-base sm:text-lg lg:text-xl font-bold text-gray-900 mb-3 sm:mb-4 flex items-center">
                    <Upload className="h-4 w-4 sm:h-5 sm:w-5 text-blue-600 mr-2" />
                    Files Processed
                  </h3>
                  <div className="text-sm text-gray-700">
                    <p>Successfully processed <strong>{result.summary.files_processed}</strong> file(s) to enhance BRD generation.</p>
                    <p className="text-xs text-gray-600 mt-1">
                      The AI analyzed both your project description and the uploaded documents to create a more comprehensive and accurate BRD.
                    </p>
                  </div>
                </div>
              )}

              {/* AI Model Information */}
              <div className="card shadow-lg bg-gradient-to-r from-purple-50 to-indigo-50 border-purple-200">
                <h3 className="text-base sm:text-lg lg:text-xl font-bold text-gray-900 mb-3 sm:mb-4 flex items-center">
                  <Brain className="h-4 w-4 sm:h-5 sm:w-5 text-purple-600 mr-2" />
                  AI Generation Details
                </h3>
                <div className="text-sm text-gray-700 space-y-2">
                  <p><strong>AI Provider:</strong> <span className="text-purple-600 font-semibold">{result.llm_provider_used}</span></p>
                  <p><strong>Model:</strong> <span className="text-indigo-600 font-semibold">gemini-2.0-flash</span></p>
                  <p className="text-xs text-gray-600">
                    This BRD was generated using Google's advanced Gemini AI model, providing intelligent analysis and comprehensive business requirements documentation.
                  </p>
                </div>
              </div>

              {/* Enhanced BRD Content */}
              <div className="card shadow-lg">
                <h3 className="text-base sm:text-lg lg:text-xl font-bold text-gray-900 mb-3 sm:mb-4 flex items-center">
                  <FileText className="h-4 w-4 sm:h-5 sm:w-5 text-indigo-600 mr-2" />
                  Generated BRD Content
                </h3>
                <div className="bg-gray-50 rounded-lg p-2 sm:p-3 lg:p-4 max-h-48 sm:max-h-64 lg:max-h-80 overflow-y-auto border border-gray-200">
                  <pre className="whitespace-pre-wrap text-xs sm:text-sm text-gray-800 font-mono leading-relaxed">
                    {result.brd_markdown}
                  </pre>
                </div>
              </div>

              {/* Enhanced Download Options */}
              <div className="card shadow-lg bg-gradient-to-r from-gray-50 to-blue-50">
                <h3 className="text-base sm:text-lg lg:text-xl font-bold text-gray-900 mb-3 sm:mb-4 flex items-center">
                  <Download className="h-4 w-4 sm:h-5 sm:w-5 text-green-600 mr-2" />
                  Download Options
                </h3>
                <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
                  <button
                    onClick={downloadBRD}
                    className="flex-1 btn-primary flex items-center justify-center space-x-2 py-2.5 sm:py-3 text-xs sm:text-sm lg:text-base font-semibold rounded-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
                  >
                    <FileText className="h-3 w-3 sm:h-4 sm:w-4" />
                    <span>Download BRD (Markdown)</span>
                  </button>
                  <button
                    onClick={downloadPDF}
                    disabled={isGeneratingPDF}
                    className="flex-1 btn-secondary flex items-center justify-center space-x-2 py-2.5 sm:py-3 text-xs sm:text-sm lg:text-base font-semibold rounded-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isGeneratingPDF ? (
                      <>
                        <div className="animate-spin rounded-full h-3 w-3 sm:h-4 sm:w-4 border-b-2 border-white"></div>
                        <span>Generating PDF...</span>
                      </>
                    ) : (
                      <>
                        <Download className="h-3 w-3 sm:h-4 sm:w-4" />
                        <span>Download PDF</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  )
}

export default Dashboard
